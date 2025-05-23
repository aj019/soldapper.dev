# Virtual Assistant Web App

A web application that acts as a virtual assistant using Fetch.ai uAgent and Helius for on-chain data analysis.

# Demo
https://github.com/user-attachments/assets/e0c18618-06f3-4e74-a920-5ca2fcfa215e

## Features
- Real-time on-chain data analysis
- AI-powered virtual assistant
- Modern web interface
- Secure authentication
- Helius API integration

## Setup

1. Clone the repository
2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Create a `.env` file with your API keys:
   ```
   HELIUS_API_KEY=your_helius_api_key
   FETCH_AI_API_KEY=your_fetch_ai_api_key
   SUBSTREAMS_API_KEY=your_substream_ai_api_key
   ASI1_API_KEY=your_fetch_asi_llm_api_key
   ```
5. Start the backend server:
   ```bash
   uvicorn app.main:app --reload
   ```
6. Start the frontend:
   ```bash
   cd frontend
   npm install
   npm start
   ```

## Project Structure
- `app/` - Backend FastAPI application
- `frontend/` - React frontend application
- `agents/` - Fetch.ai uAgent implementations 
