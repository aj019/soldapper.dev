from uagents import Agent, Context
from wallet_models import WalletCheckRequest, WalletCheckResponse
import asyncio
# Replace this with your Wallet Agent's actual address (see terminal after you run it)
TARGET_AGENT_DID = "agent1qvemdtgcktv9q9f9mgv3xjr689wghzprujp62mg73a08pezyy6dzzzwuhsc"

# Replace this with your actual Solana wallet address
MY_WALLET_ADDRESS = "ENr8q2ZddGGBpHLMCTD5pnzDb3MSPHwkk8cpvHJV9qTd"

# Create the client agent
client = Agent(
    name="wallet-client",
    seed="wallet client demo seed",
    port=5054,
    endpoint=["http://localhost:5054/submit"],  # Listen on both localhost and all interfaces
)

async def send_wallet_check(ctx: Context):
    print("---- Sending wallet check ----")
    try:
        ctx.logger.info(f"Sending wallet address to wallet analyzer agent...")
        await ctx.send(TARGET_AGENT_DID, WalletCheckRequest(wallet_address=MY_WALLET_ADDRESS))
    except Exception as e:
        ctx.logger.error(f"Error sending message: {e}")

# Handle the response from the wallet analyzer
@client.on_message(model=WalletCheckResponse)
async def handle_response(ctx: Context, sender: str, msg: WalletCheckResponse):
    print(f"\n📊 Received wallet analysis from {sender}:")
    print(msg.summary)
    global summary
    summary = msg.summary
    print()  # Empty line for better readability

#client.on_interval(period=5.0)(send_wallet_check)

@client.on_event('startup')
async def startup_handler(ctx: Context):
    print("🚀 Starting wallet client...")
    # await send_wallet_check(ctx)

@client.on_rest_get("/get/wallet_analysis", WalletCheckResponse)
async def get_messages(ctx: Context):
    await send_wallet_check(ctx)
    global summary
    for _ in range(10):  # wait up to 5 seconds
        if summary:
            return WalletCheckResponse(summary=summary)
        
        await asyncio.sleep(0.5)
    

if __name__ == "__main__":
    try:
        print("🚀 Starting wallet client...")
        client.run()
    except KeyboardInterrupt:
        print("\n👋 Shutting down wallet client...")
    except Exception as e:
        print(f"❌ Error running client: {e}")
