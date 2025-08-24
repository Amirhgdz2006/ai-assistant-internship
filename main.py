import os
from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, Request , HTTPException , status
from fastapi.responses import JSONResponse
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from starlette.middleware.sessions import SessionMiddleware
from fastapi.middleware.cors import CORSMiddleware

import routers.user
import routers.ai
import routers.google_auth

from core.limiter import limiter

secret_key = os.getenv("SECRET_KEY")

app = FastAPI()

origins = ["http://localhost:8000", "http://localhost:3000", "http://127.0.0.1:5173"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  
    allow_credentials=True, 
    allow_methods=["*"],    
    allow_headers=["*"]
)

app.add_middleware(SessionMiddleware, secret_key=secret_key)
app.state.limiter = limiter
app.add_middleware(SlowAPIMiddleware)

@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS,detail="Too many requests. Please wait a few seconds and try again.")

app.include_router(routers.user.router)
app.include_router(routers.ai.router)
app.include_router(routers.google_auth.router)

@app.get("/", tags=["Root"])
def intro():
    return {"message": "Welcome to the FastAPI application"}
