from uagents import Agent, Protocol, Context
from uagents_core.contrib.protocols.chat import (
    ChatAcknowledgement,
    ChatMessage,
    EndSessionContent,
    TextContent,
    chat_protocol_spec,
)
from datetime import datetime
from uuid import uuid4

# Create a second agent
sender_agent = Agent(name="sender", seed="sender_seed", port=8082, endpoint=["http://localhost:8082/submit"])

# Use the same chat protocol


@sender_agent.on_interval(period=5)  # wait a few seconds and then send message
async def send_message(ctx: Context):
    await ctx.send(
        "agent1q230e8xjs6wga8hzv7kt4963mrg67ksqkn84e27lss6tqya7az9ks49snzj",  # replace with your agent's address
        ChatMessage(
            timestamp=datetime.utcnow(),
            msg_id=uuid4(),
            content=[
                TextContent(type="text", text="What tokens are present in my wallet?")
            ]
        )
    )

@sender_agent.on_message(model=ChatMessage)
async def handle_response(ctx: Context, sender: str, msg: ChatMessage):
    ctx.logger.info(f"Received response from {sender}: {msg}")
    text_content = ""
    for item in msg.content:
        if isinstance(item, TextContent):
            text_content += item.text
    print(f"Response received: {text_content}")


sender_agent.run()
