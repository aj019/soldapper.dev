from openai import OpenAI
from typing import Dict, Any, List
import json
from app.core.config import settings
from app.core.monitoring import monitoring

class OpenAIService:
    def __init__(self):
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
        self.conversation_history: Dict[str, List[Dict[str, str]]] = {}

    async def analyze_query(self, query: str, session_id: str = None) -> Dict[str, Any]:
        """Analyze the query using OpenAI to extract structured information."""
        try:
            system_prompt = """
            You are a blockchain data analysis assistant. Analyze the query and extract:
            1. Query type (balance/transaction/nft/analysis)
            2. Solana addresses mentioned
            3. Time period if specified
            4. Specific tokens or NFTs mentioned
            5. Any specific metrics or analysis requested
            
            Output in JSON format with the following structure:
            {
                "intent": "balance|transaction|nft|analysis",
                "addresses": ["address1", "address2"],
                "time_period": "24h|7d|30d|1y",
                "tokens": ["token1", "token2"],
                "metrics": ["metric1", "metric2"],
                "confidence": 0.0-1.0
            }
            """

            # Get conversation history if session exists
            messages = [{"role": "system", "content": system_prompt}]
            if session_id and session_id in self.conversation_history:
                messages.extend(self.conversation_history[session_id])
            messages.append({"role": "user", "content": query})

            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=messages,
                temperature=0.3,
                response_format={"type": "json_object"}
            )

            # Parse the response
            analysis = json.loads(response.choices[0].message.content)

            # Update conversation history
            if session_id:
                if session_id not in self.conversation_history:
                    self.conversation_history[session_id] = []
                self.conversation_history[session_id].extend([
                    {"role": "user", "content": query},
                    {"role": "assistant", "content": response.choices[0].message.content}
                ])
                # Keep only last 10 messages to maintain context
                self.conversation_history[session_id] = self.conversation_history[session_id][-10:]

            return analysis

        except Exception as e:
            monitoring.log_error(e, "analyze_query")
            return {
                "intent": "general",
                "addresses": [],
                "time_period": None,
                "tokens": [],
                "metrics": [],
                "confidence": 0.0
            }

    async def generate_response(self, data: Dict[str, Any], query_analysis: Dict[str, Any]) -> str:
        """Generate a natural language response using OpenAI."""
        try:
            system_prompt = """
            You are a blockchain data analysis assistant. Generate a clear, concise, and informative response 
            based on the provided data and query analysis. Focus on:
            1. Answering the specific query
            2. Highlighting important metrics
            3. Providing context where relevant
            4. Using natural, conversational language
            """

            data_summary = json.dumps(data, indent=2)
            query_context = json.dumps(query_analysis, indent=2)

            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"""
                    Query Analysis: {query_context}
                    Data: {data_summary}
                    
                    Generate a natural response that answers the query using this data.
                    """}
                ],
                temperature=0.7
            )

            return response.choices[0].message.content

        except Exception as e:
            monitoring.log_error(e, "generate_response")
            return "I apologize, but I encountered an error while generating the response."

    def clear_conversation_history(self, session_id: str):
        """Clear conversation history for a specific session."""
        if session_id in self.conversation_history:
            del self.conversation_history[session_id]

# Initialize OpenAI service
openai_service = OpenAIService() 