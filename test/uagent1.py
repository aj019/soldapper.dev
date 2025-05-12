#imprting Agent and Context from uagents
from uagents import Agent, Context
#importing Message from agent_models
from agent_models import Message

my_first_agent = Agent(
    name='My First Agent',
    port=5050,
    endpoint=['http://localhost:5050/submit']
)

second_agent = 'agent1qwzscfljtdkzreuxj42y47kfnjg48kj3lnhe3lll8hgmtgfm8ghl73hxurv'

@my_first_agent.on_event('startup')
async def startup_handler(ctx: Context):
    #logging the name and address of the agent
    ctx.logger.info(f'My name is {ctx.agent.name} and my address is {ctx.agent.address}')
    #sending a message to the second agent
    await ctx.send(second_agent, Message(message='Hi Second Agent, this is the first agent.'))

@my_first_agent.on_message(model=Message)
async def message_handler(ctx: Context, sender: str, msg: Message):
    ctx.logger.info(f'I have received a message from {sender}.')
    ctx.logger.info(f'I have received a message {msg.message}.')
    await ctx.send(sender, Message(message='Hi Second Agent, i received your message.'))

if __name__ == "__main__":
    my_first_agent.run()