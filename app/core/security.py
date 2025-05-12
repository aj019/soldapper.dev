from fastapi import Security, HTTPException, status, Request
from fastapi.security import APIKeyHeader
from fastapi.responses import JSONResponse
from typing import Optional
import time
from app.core.config import settings

API_KEY_NAME = "X-API-Key"
api_key_header = APIKeyHeader(name=API_KEY_NAME)

# Rate limiting storage
rate_limit_storage = {}

async def get_api_key(api_key_header: str = Security(api_key_header)):
    if api_key_header != settings.API_KEY:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid API key"
        )
    return api_key_header

async def rate_limit_middleware(request: Request, call_next):
    client_ip = request.client.host
    current_time = time.time()
    
    # Check if client exists in storage
    if client_ip in rate_limit_storage:
        last_request_time, request_count = rate_limit_storage[client_ip]
        
        # Reset counter if more than 1 minute has passed
        if current_time - last_request_time > 60:
            rate_limit_storage[client_ip] = (current_time, 1)
        else:
            # Check if rate limit exceeded
            if request_count >= 60:  # 60 requests per minute
                return JSONResponse(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    content={"detail": "Rate limit exceeded. Please try again later."}
                )
            # Increment request count
            rate_limit_storage[client_ip] = (last_request_time, request_count + 1)
    else:
        # Initialize new client
        rate_limit_storage[client_ip] = (current_time, 1)
    
    response = await call_next(request)
    return response 