from datetime import datetime
from uuid import uuid4

import json
from datetime import datetime, timezone
import httpx
from openai import OpenAI, BadRequestError
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from uagents import Context, Protocol, Agent
from uagents_core.contrib.protocols.chat import (
    ChatAcknowledgement,
    ChatMessage,
    EndSessionContent,
    TextContent,
    chat_protocol_spec,
)
import re


# Explicitly create an httpx client
httpx_client = httpx.Client()

client = OpenAI(
    # By default, we are using the ASI-1 LLM endpoint and model
    base_url='https://api.asi1.ai/v1',

    # You can get an ASI-1 api key by creating an account at https://asi1.ai/dashboard/api-keys
    api_key='sk_52e5e22254c44ed9b9a0cf199e11e3ba3086c47c4eed49a184436a61a9cde05f',
    http_client=httpx_client,
)

agent = Agent(name="decharge", seed="decharge_sed", port=8084, endpoint=["http://localhost:8084/submit"])

def load_data(file_path):
    with open(file_path, 'r') as file:
        return json.load(file)

def get_data_between_timestamps(data, start_timestamp, end_timestamp):
    start_dt = datetime.fromtimestamp(start_timestamp, tz=timezone.utc)
    end_dt = datetime.fromtimestamp(end_timestamp, tz=timezone.utc)
    filtered_data = [
        item for item in data
        if start_dt <= datetime.fromisoformat(item['timestamp'].replace('Z', '+00:00')) <= end_dt
    ]
    return filtered_data


# We define the handler for the chat messages that are sent to your agent
@agent.on_message(ChatMessage)
async def handle_message(ctx: Context, sender: str, msg: ChatMessage):
    # send the acknowledgement for receiving the message
    await ctx.send(
        sender,
        ChatAcknowledgement(timestamp=datetime.now(), acknowledged_msg_id=msg.msg_id),
    )

    # collect up all the text chunks
    text = ''
    for item in msg.content:
        if isinstance(item, TextContent):
            text += item.text

    # query the model based on the user question
    response = 'I am afraid something went wrong and I am unable to answer your question at the moment'

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        retry=retry_if_exception_type(BadRequestError),
        reraise=True,
    )
    def format_response(json_data):
        r = client.chat.completions.create(
            model="asi1-mini",
            messages=[
                {"role": "system", "content": f"""
                Format the below json data in to a human readable format. The response should be in html format.
                {json_data}
                """},
                {"role": "user", "content": text},
            ],
            max_tokens=2048,
        )        
        print("Formatted response:",r.choices[0].message.content)
        return r.choices[0].message.content

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        retry=retry_if_exception_type(BadRequestError),
        reraise=True,
    )
    # This function extracts the start and end timestamps from the user's message
    def query_model():
        r = client.chat.completions.create(
            model="asi1-mini",
            messages=[
                {"role": "system", "content": f"""
                You are a data extractor agent. Your job is to extract two timestamps from the user's 
                 message and return the two timestamps in the json format
                  "eg {{'start_timestamp': '1746090000', 'end_timestamp': '1746091800'}}"
                  The user might give timestamps in any format. For eg 'Show me car data for May 1st between 9:05Am and 9:15Am'. 
                 You need to extract the time from the user's message and convert them to unix timestamps
                If the user does not provide two timestamps, return empty string
                """},
                {"role": "user", "content": text},
            ],
            max_tokens=2048,
        )
        print(r.choices[0].message.content)
        content = r.choices[0].message.content.strip()
        if not content:
            return "Could not extract timestamps. Please provide start and end timestamps"
        # Try to extract JSON object using regex
        match = re.search(r"\{.*\}", content)
        if not match:
            return "Could not extract timestamps. Please provide start and end timestamps"
        json_str = match.group(0).replace("'", '"')
        try:
            json_data = json.loads(json_str)
        except Exception:
            return "Could not extract timestamps. Please provide start and end timestamps"
        #check if json_data is a dictionary
        if isinstance(json_data, dict):
            data = load_data('knowledge_base/synthetic_obd_data_24h.json')
            start_timestamp = int(json_data['start_timestamp'])
            end_timestamp = int(json_data['end_timestamp'])
            print("Start timestamp:",start_timestamp,"End timestamp:",end_timestamp)
            result = get_data_between_timestamps(data, start_timestamp, end_timestamp)
            #pass only 3 random samples from the result
            result = result[:3]
            print("Result:",result)
            return format_response(str(result))
        else:
            return "Could not extract timestamps. Please provide start and end timestamps"


    try:
        response = query_model()
    except Exception as e:
        ctx.logger.exception('Error querying model')
        print(f"OpenAI API Error: {e}")

    # send the response back to the user
    await ctx.send(sender, ChatMessage(
        timestamp=datetime.utcnow(),
        msg_id=uuid4(),
        content=[
            # we send the contents back in the chat message
            TextContent(type="text", text=response),
            # we also signal that the session is over, this also informs the user that we are not recording any of the
            # previous history of messages.
            EndSessionContent(type="end-session"),
        ]
    ))

agent.run()



