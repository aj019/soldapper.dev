from uagents import Agent, Protocol, Context
from uagents_core.contrib.protocols.chat import (
    ChatAcknowledgement,
    ChatMessage,
    EndSessionContent,
    TextContent,
    chat_protocol_spec,
)
from wallet_agent import WalletCheckResponse
from datetime import datetime
from uuid import uuid4
import asyncio

# Initialize summary as None
summary = None

# Create a second agent
sender_agent = Agent(name="sender", seed="sender_seed", port=8082, endpoint=["http://localhost:8082/submit"])

# Use the same chat protocol


# @sender_agent.on_interval(period=5)  # wait a few seconds and then send message
# async def send_message(ctx: Context):
#     await ctx.send(
#         "agent1q230e8xjs6wga8hzv7kt4963mrg67ksqkn84e27lss6tqya7az9ks49snzj",  # replace with your agent's address
#         ChatMessage(
#             timestamp=datetime.utcnow(),
#             msg_id=uuid4(),
#             content=[
#                 TextContent(type="text", text="What tokens are present in my wallet?")
#             ]
#         )
#     )

@sender_agent.on_message(model=ChatMessage)
async def handle_response(ctx: Context, sender: str, msg: ChatMessage):
    ctx.logger.info(f"Received response from {sender}: {msg}")
    text_content = ""
    for item in msg.content:
        if isinstance(item, TextContent):
            text_content += item.text
    global summary
    print("Received response from wallet agent:",text_content)
    summary = text_content


@sender_agent.on_rest_post("/post/query_response",WalletCheckResponse ,WalletCheckResponse)
async def post_messages(ctx: Context, request_data: WalletCheckResponse):
    global summary
    # Reset summary before sending new message
    summary = None
    
    message_text = request_data.summary
    
    await ctx.send(
        "agent1q230e8xjs6wga8hzv7kt4963mrg67ksqkn84e27lss6tqya7az9ks49snzj",  # replace with your agent's address
        ChatMessage(
            timestamp=datetime.utcnow(),
            msg_id=uuid4(),
            content=[
                TextContent(type="text", text=message_text)
            ]
        )
    )
    
    # Wait for response with timeout
    for _ in range(10):  # wait up to 5 seconds
        if summary is not None:
            response = summary
            summary = None  # Reset for next request
            return WalletCheckResponse(summary=response)
        await asyncio.sleep(5)
    
    # If no response received within timeout
    return WalletCheckResponse(summary="No response received from wallet agent. Please try again.")

sender_agent.run()
