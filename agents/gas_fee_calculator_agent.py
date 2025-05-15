import requests
import subprocess
from uagents import Agent, Context, Protocol, Model
from wallet_models import WalletCheckRequest, WalletCheckResponse, SubstreamRequest, SubstreamResponse

# --- Agent Setup ---
agent = Agent(
    name="gas-fee-calculator",
    seed="gas-fee-calculator agent seed",
    endpoint=["http://localhost:5055/submit"],  # Listen on both localhost and all interfaces
    port=5055,
)

@agent.on_event('startup')
async def startup_handler(ctx: Context):
    print("🚀 Starting substream runner agent at address: ", ctx.agent.address)

@agent.on_message(model=SubstreamRequest)
async def handle_request(ctx: Context, sender: str, msg: SubstreamRequest):
    print("Request received")
    ctx.logger.info(f"Running substream: {msg.module} on {msg.package_url}")
    try:
        result = subprocess.run(
            [
                "substreams", "run", msg.module,
                msg.package_url,
                "--start-block", str(msg.start_block),
                "--stop-block", str(msg.stop_block)
            ],
            capture_output=True,
            text=True,
            timeout=60
        )
        if result.returncode == 0:
            ctx.logger.info("Substream run successful")
            await ctx.send(sender, SubstreamResponse(output=result.stdout))
        else:
            ctx.logger.error(f"Substream run failed: {result.stderr}")
            await ctx.send(sender, SubstreamResponse(output=result.stderr))
    except Exception as e:
        ctx.logger.error(f"Exception running substream: {e}")
        await ctx.send(sender, SubstreamResponse(output=str(e)))


if __name__ == "__main__":
    try:
        print("🚀 Starting gas fee calculator agent...")
        agent.run()
    except KeyboardInterrupt:
        print("\n👋 Shutting down gas fee calculator agent...")
    except Exception as e:
        print(f"❌ Error running agent: {e}")