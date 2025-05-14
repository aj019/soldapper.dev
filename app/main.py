from fastapi import FastAPI, Request
from datetime import datetime
from agents.test_agent import test_agent, QueryMessage, ResponseMessage
from uagents import Context
app = FastAPI()

from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)


@app.get("/")
async def root():
    return {"message": "Hello"}


@app.post("/test")
async def test(request: Request):
    data = await request.json()
    return {"message": "Test", "data": data}

@app.post("/query")
async def query(request: Request):
    data = await request.json()
    response = await test_agent.send(
        test_agent.address,
        QueryMessage(
            text=data["text"]
        )
    )
    return {
        "text": response.text,
        "sender": "assistant",
        "timestamp": datetime.now().isoformat()
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 