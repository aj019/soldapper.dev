from uagents import Agent, Context
from agent_models import Message

my_second_agent = Agent(
    name='My Second Agent',
    port=5051,
    endpoint=['http://localhost:5051/submit']
)

@my_second_agent.on_event('startup')
async def startup_handler(ctx: Context):
    ctx.logger.info(f'My name is {ctx.agent.name} and my address is {ctx.agent.address}')

@my_second_agent.on_message(model=Message)
async def message_handler(ctx: Context, sender: str, msg: Message):
    ctx.logger.info(f'I have received a message from {sender}.')
    ctx.logger.info(f'I have received a message {msg.message}.')
    await ctx.send(sender, Message(message='Hi First Agent, i received your message.'))

if __name__ == "__main__":
    my_second_agent.run()