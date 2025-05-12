from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from app.routers import chain_data, assistant
from app.core.config import settings
from app.core.security import rate_limit_middleware
from app.core.monitoring import monitoring
import time

app = FastAPI(
    title="Virtual Assistant API",
    description="API for virtual assistant with on-chain data analysis",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add rate limiting middleware
@app.middleware("http")
async def add_rate_limit_middleware(request: Request, call_next):
    start_time = time.time()
    response = await rate_limit_middleware(request, call_next)
    duration = time.time() - start_time
    
    # Log request
    monitoring.log_request(
        endpoint=request.url.path,
        status="success" if response.status_code < 400 else "error",
        duration=duration
    )
    
    return response

# Include routers
app.include_router(chain_data.router, prefix="/api/chain", tags=["chain-data"])
app.include_router(assistant.router, prefix="/api/assistant", tags=["assistant"])

@app.get("/")
async def root():
    return {"message": "Welcome to Virtual Assistant API"}

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "version": "1.0.0",
        "analytics": monitoring.get_analytics()
    } 