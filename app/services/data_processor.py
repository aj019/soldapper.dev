from typing import Dict, Any, List
from datetime import datetime
import json

class DataProcessor:
    def process_chain_data(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process and transform raw chain data into a more readable format."""
        try:
            processed_data = {
                "address": raw_data.get("address", ""),
                "summary": self._generate_summary(raw_data),
                "balances": self._process_balances(raw_data.get("balances", [])),
                "transactions": self._process_transactions(raw_data.get("recent_transactions", [])),
                "last_updated": datetime.utcnow().isoformat()
            }
            return processed_data
        except Exception as e:
            raise ValueError(f"Error processing chain data: {str(e)}")

    def _generate_summary(self, data: Dict[str, Any]) -> str:
        """Generate a human-readable summary of the chain data."""
        balances = data.get("balances", [])
        transactions = data.get("recent_transactions", [])
        
        total_balance = sum(float(bal.get("amount", 0)) for bal in balances)
        recent_tx_count = len(transactions)
        
        return f"Address has a total balance of {total_balance} tokens across {len(balances)} assets. " \
               f"Recent activity shows {recent_tx_count} transactions in the last period."

    def _process_balances(self, balances: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Process and format balance data."""
        processed_balances = []
        for balance in balances:
            processed_balance = {
                "token": balance.get("token", "Unknown"),
                "amount": float(balance.get("amount", 0)),
                "value_usd": float(balance.get("value_usd", 0)),
                "percentage_change": float(balance.get("percentage_change", 0))
            }
            processed_balances.append(processed_balance)
        return processed_balances

    def _process_transactions(self, transactions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Process and format transaction data."""
        processed_transactions = []
        for tx in transactions:
            processed_tx = {
                "hash": tx.get("hash", ""),
                "timestamp": tx.get("timestamp", ""),
                "type": tx.get("type", "Unknown"),
                "amount": float(tx.get("amount", 0)),
                "status": tx.get("status", "Unknown")
            }
            processed_transactions.append(processed_tx)
        return processed_transactions

    def format_for_display(self, data: Dict[str, Any]) -> str:
        """Format data for display in the chat interface."""
        try:
            summary = data.get("summary", "")
            balances = data.get("balances", [])
            
            display_text = f"{summary}\n\nToken Balances:\n"
            for balance in balances:
                display_text += f"- {balance['token']}: {balance['amount']} (${balance['value_usd']})\n"
            
            return display_text
        except Exception as e:
            return f"Error formatting data: {str(e)}" 