# This is a test agent returns a text response on query
from uagents import Agent, Context, Model
from fastapi.responses import JSONResponse

test_agent = Agent(
    name="test_agent",
    seed="test_agent_seed",
    port=5055,
    endpoint=["http://localhost:5055"],
)

class QueryMessage(Model):
    text: str

class ResponseMessage(Model):
    text: str

@test_agent.on_message(model=QueryMessage)
async def handle_query(ctx: Context, sender: str, msg: QueryMessage):
    ctx.logger.info(f"Received query from {sender}: {msg}")
    await ctx.send(sender, ResponseMessage(text="Hello, how can I help you today?"))

@test_agent.on_event('startup')
async def startup_handler(ctx: Context):
    ctx.logger.info("Test agent started")

@test_agent.on_rest_get("/rest/get_messages", ResponseMessage)
async def get_messages(ctx: Context):
    return ResponseMessage(text="Hello Messages")

if __name__ == "__main__":
    test_agent.run()