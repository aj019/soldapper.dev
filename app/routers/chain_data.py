from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any
import requests
from app.core.config import settings

router = APIRouter()

@router.get("/summary/{address}")
async def get_chain_summary(address: str):
    """
    Get a summary of on-chain data for a given address using Helius API
    """
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
        
        return {
            "address": address,
            "balances": balances_data,
            "recent_transactions": transactions_data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/nft/{address}")
async def get_nft_data(address: str):
    """
    Get NFT data for a given address
    """
    try:
        headers = {
            "Authorization": f"Bearer {settings.HELIUS_API_KEY}",
            "Content-Type": "application/json"
        }
        
        nft_url = f"{settings.HELIUS_API_URL}/addresses/{address}/nfts"
        response = requests.get(nft_url, headers=headers)
        return response.json()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 