from uagents import Agent
from wallet_models import SubstreamRequest

sender = Agent(
    name="substream-request",
    seed="substream-request agent seed",
    endpoint=["http://localhost:5056/submit"],  # Listen on both localhost and all interfaces
    port=5056,
)

receiver_address = "agent1qfhmxt9cv4ddsz7p2p6cna2ve6zezulqp4ycml7v9slxrj9cf5smkpzwswy"  # Use actual address

@sender.on_event("startup")
async def send(ctx):
    req = SubstreamRequest(
        start_block=210000000,
        stop_block=210000010,
        module="map_wallet_gas_fees",
        package_url="https://spkg.io/v1/packages/solana_gas_substream/v0.1.0"
    )
    await ctx.send(receiver_address, req)
    print("🚀 Substream request sent successfully! ",receiver_address)

sender.run()
