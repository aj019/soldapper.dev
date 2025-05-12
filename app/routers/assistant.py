from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any, List
from uagents import Agent, Context, Model
from uagents.setup import fund_agent_if_low
from app.core.security import get_api_key
from app.services.data_processor import DataProcessor
from app.services.openai_service import openai_service
from app.core.monitoring import monitoring
import requests
import json
from datetime import datetime
from pydantic import BaseModel

router = APIRouter()
data_processor = DataProcessor()

# Define message models
class QueryMessage(Model):
    text: str
    context: Dict[str, Any] = {}
    session_id: str = None

class ResponseMessage(Model):
    text: str
    data: Dict[str, Any] = {}
    timestamp: str
    analysis: Dict[str, Any] = {}

# Initialize the Fetch.ai agent
agent = Agent(
    name="virtual_assistant",
    seed="virtual_assistant_seed_phrase",
    port=8000,
    endpoint=["http://127.0.0.1:8000/submit"],
)

# Store conversation context
conversation_context = {}

@agent.on_interval(period=3600.0)
async def check_balance(ctx: Context):
    await fund_agent_if_low(ctx)

@agent.on_message(model=QueryMessage)
async def handle_query(ctx: Context, sender: str, msg: QueryMessage):
    try:
        # Analyze query using OpenAI
        query_analysis = await openai_service.analyze_query(msg.text, msg.session_id)
        
        # Process the query based on analysis
        response = await process_query(msg.text, query_analysis)
        
        # Generate natural language response
        response_text = await openai_service.generate_response(
            response.get("data", {}),
            query_analysis
        )
        
        # Send response back
        await ctx.send(
            sender,
            ResponseMessage(
                text=response_text,
                data=response.get("data", {}),
                timestamp=datetime.utcnow().isoformat(),
                analysis=query_analysis
            )
        )
    except Exception as e:
        monitoring.log_error(e, "handle_query")
        await ctx.send(
            sender,
            ResponseMessage(
                text=f"Sorry, I encountered an error: {str(e)}",
                timestamp=datetime.utcnow().isoformat()
            )
        )

async def process_query(query: str, analysis: Dict[str, Any]) -> Dict[str, Any]:
    """Process user query based on OpenAI analysis."""
    try:
        if analysis["confidence"] < 0.5:
            return {
                "text": "I'm not sure I understood your query. Could you please rephrase it?",
                "data": {}
            }
            
        # Get chain data if address is present
        if analysis["addresses"]:
            address = analysis["addresses"][0]  # Use first address found
            chain_data = await get_chain_data(
                address,
                time_period=analysis.get("time_period")
            )
            processed_data = data_processor.process_chain_data(chain_data)
            
            # Filter data based on analysis
            if analysis["tokens"]:
                processed_data["balances"] = [
                    bal for bal in processed_data["balances"]
                    if bal["token"] in analysis["tokens"]
                ]
            
            if analysis["time_period"]:
                processed_data["transactions"] = filter_transactions_by_period(
                    processed_data["transactions"],
                    analysis["time_period"]
                )
            
            return {
                "data": processed_data
            }
        else:
            return {
                "text": "I can help you analyze on-chain data. Please provide a Solana address to get started.",
                "data": {}
            }
    except Exception as e:
        monitoring.log_error(e, "process_query")
        raise HTTPException(status_code=500, detail=str(e))

def filter_transactions_by_period(transactions: List[Dict[str, Any]], period: str) -> List[Dict[str, Any]]:
    """Filter transactions based on time period."""
    from datetime import datetime, timedelta
    
    now = datetime.utcnow()
    if period == "24h":
        cutoff = now - timedelta(hours=24)
    elif period == "7d":
        cutoff = now - timedelta(days=7)
    elif period == "30d":
        cutoff = now - timedelta(days=30)
    elif period == "1y":
        cutoff = now - timedelta(days=365)
    else:
        return transactions
        
    return [
        tx for tx in transactions
        if datetime.fromisoformat(tx["timestamp"]) > cutoff
    ]

async def get_chain_data(address: str, time_period: str = None) -> Dict[str, Any]:
    """Fetch chain data from Helius API."""
    try:
        headers = {
            "Authorization": f"Bearer {settings.HELIUS_API_KEY}",
            "Content-Type": "application/json"
        }
        
        # Get token balances
        balances_url = f"{settings.HELIUS_API_URL}/addresses/{address}/balances"
        balances_response = requests.get(balances_url, headers=headers)
        balances_data = balances_response.json()
        
        # Get transaction history
        transactions_url = f"{settings.HELIUS_API_URL}/addresses/{address}/transactions"
        transactions_response = requests.get(transactions_url, headers=headers)
        transactions_data = transactions_response.json()
        
        # Get NFT data
        nft_url = f"{settings.HELIUS_API_URL}/addresses/{address}/nfts"
        nft_response = requests.get(nft_url, headers=headers)
        nft_data = nft_response.json()
        
        return {
            "address": address,
            "balances": balances_data,
            "transactions": transactions_data,
            "nfts": nft_data
        }
    except Exception as e:
        monitoring.log_error(e, "get_chain_data")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/query")
async def process_user_query(
    query: Dict[str, str],
    api_key: str = Depends(get_api_key)
):
    """Process user query through the Fetch.ai agent with OpenAI integration."""
    try:
        # Send query to agent
        response = await agent.send(
            agent.address,
            QueryMessage(
                text=query["text"],
                session_id=query.get("session_id")
            )
        )
        
        # Update conversation context
        if "session_id" in query:
            conversation_context[query["session_id"]] = response.context
        
        return response
    except Exception as e:
        monitoring.log_error(e, "process_user_query")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/status")
async def get_agent_status(api_key: str = Depends(get_api_key)):
    """Get the status of the Fetch.ai agent."""
    return {
        "status": "active",
        "agent_name": agent.name,
        "endpoint": agent.endpoint,
        "address": str(agent.address)
    } 