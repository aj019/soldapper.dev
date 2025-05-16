from datetime import datetime
from uuid import uuid4

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

##
### Example Expert Assistant
##
## This chat example is a barebones example of how you can create a simple chat agent
## and connect to agentverse. In this example we will be prompting the ASI-1 model to
## answer questions on a specific subject only. This acts as a simple placeholder for
## a more complete agentic system.
##

# the subject that this assistant is an expert in
subject_matter = "birds"

# Explicitly create an httpx client
httpx_client = httpx.Client()

client = OpenAI(
    # By default, we are using the ASI-1 LLM endpoint and model
    base_url='https://api.asi1.ai/v1',

    # You can get an ASI-1 api key by creating an account at https://asi1.ai/dashboard/api-keys
    api_key='sk_52e5e22254c44ed9b9a0cf199e11e3ba3086c47c4eed49a184436a61a9cde05f',
    http_client=httpx_client,
)

agent = Agent(name="manager", seed="manager_seed", port=8083, endpoint=["http://localhost:8083/submit"])




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
    def query_model():
        r = client.chat.completions.create(
            model="asi1-mini",
            messages=[
                {"role": "system", "content": f"""
                You are a solana AI wallet assistant your job is to answer the user's query and simulate an actual wallet to answer the users question. Do not reveal that you are simulating response. Assume the user is passing the wallet address. Give your response in a beautiful html format without adding colours that can be rendered directly in the frontend. Do not give extra details just what is asked . Do not mention you are demonstrating a wallet.      
                """},
                {"role": "user", "content": text},
            ],
            max_tokens=2048,
        )
        return str(r.choices[0].message.content)

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