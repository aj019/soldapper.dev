import requests
from uagents import Agent, Context, Protocol, Model
from wallet_models import WalletCheckRequest, WalletCheckResponse

# --- Fetch Data from Helius ---
def get_wallet_summary(address: str) -> str:
    api_key = "88e733b6-4747-4c9e-9e95-302504525433"  # 🔐 Replace this with your real key
    url = "https://mainnet.helius-rpc.com?api-key=" + api_key

    print("Hitting Helius API")
    try:
        # Send a POST request to the Helius API with the specified URL, payload, and headers
        response = requests.post(url, json={
            "jsonrpc": "2.0",
            "id": "1",
            "method": "getTokenAccountsByOwner",
            "params": [
                address,
                {"programId": "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA"},  # SPL Token Program ID
                {"encoding": "jsonParsed"}
            ]
        }, headers={"Content-Type": "application/json"})
        
        # Raise an exception if the request was unsuccessful
        response.raise_for_status()
        # Parse the JSON response from the API
        data = response.json()
        # Print the response data for debugging purposes
        print("Helius API Response: ", data)
        # Check if the response contains the expected 'result' and 'value' keys
        if "result" not in data or "value" not in data["result"]:
            # Return a message indicating no tokens were found if keys are missing
            return "No tokens found for this wallet."

        # Extract the list of token accounts from the response
        token_accounts = data["result"]["value"]
        # Check if the token accounts list is empty
        if not token_accounts:
            # Return a message indicating no tokens were found if the list is empty
            return "No tokens found for this wallet."

        # Initialize a list to store summary lines for each token
        summary_lines = []

        # Iterate over each token account in the list
        for account in token_accounts:
            # Retrieve the token's amount and decimals
            amount = float(account["account"]["data"]["parsed"]["info"]["tokenAmount"]["amount"])
            decimals = account["account"]["data"]["parsed"]["info"]["tokenAmount"]["decimals"]
            # Adjust the amount based on the token's decimals
            adjusted_amount = amount / (10 ** decimals)
            # Retrieve the token's mint address
            mint = account["account"]["data"]["parsed"]["info"]["mint"]

            # Fetch token name using the provided async function
            token_name = fetch_token_name(mint)

            # Append a formatted string with the token's name and adjusted amount to the summary lines
            summary_lines.append(f"- Token: {token_name}, Balance: {adjusted_amount:,.6f}")

        # Print the summary lines for debugging purposes
        print("Summary Lines: ", summary_lines)
        # Return a formatted string with the wallet holdings summary
        return "🪙 Wallet Holdings:\n" + "\n".join(summary_lines)

    except requests.RequestException as e:
        print(f"Network error: {e}")
        return f"Error fetching wallet data: Network error"
    except Exception as e:
        print(f"Unexpected error: {e}")
        return f"Error fetching wallet data: {str(e)}"

def fetch_token_name(mint: str) -> str:
    # This function simulates the async JavaScript function to fetch token name
    try:
        response = requests.post("https://mainnet.helius-rpc.com/?api-key=88e733b6-4747-4c9e-9e95-302504525433", json={
            "jsonrpc": "2.0",
            "id": "text",
            "method": "getAsset",
            "params": {"id": mint}
        }, headers={"Content-Type": "application/json"})
        
        response.raise_for_status()
        data = response.json()
        return data["result"]["content"]["metadata"]["name"]
    except Exception as e:
        print(f"Error fetching token name: {e}")
        return mint


# --- Agent Setup ---
agent = Agent(
    name="wallet-analyzer",
    seed="wallet analyzer agent seed",
    endpoint=["http://localhost:8000/submit"],  # Listen on both localhost and all interfaces
    port=8000,
)

@agent.on_event('startup')
async def startup_handler(ctx: Context):
    print("🚀 Starting wallet analyzer agent at address: ", ctx.agent.address)

@agent.on_message(model=WalletCheckRequest)
async def handle_message(ctx: Context, sender: str, msg: WalletCheckRequest):
    try:
        print(f"✅ Received message from {sender} {msg.wallet_address}!")
        ctx.logger.info(f"Analyzing wallet: {msg.wallet_address}")
        summary = get_wallet_summary(msg.wallet_address)
        print("Final Summary: ", summary)
        await ctx.send(sender, WalletCheckResponse(summary=summary))
        print("✅ Response sent successfully!")
    except Exception as e:
        print(f"❌ Error handling message: {e}")
        ctx.logger.error(f"Error handling message: {e}")


# agent.include(wallet_protocol)

if __name__ == "__main__":
    try:
        print("🚀 Starting wallet analyzer agent...")
        agent.run()
    except KeyboardInterrupt:
        print("\n👋 Shutting down wallet analyzer agent...")
    except Exception as e:
        print(f"❌ Error running agent: {e}")
