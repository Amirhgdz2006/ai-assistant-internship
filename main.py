import os
from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from starlette.middleware.sessions import SessionMiddleware

import routers.user
import routers.ai
import routers.google_auth

from core.limiter import limiter

secret_key = os.getenv("SECRET_KEY")

app = FastAPI()

app.add_middleware(SessionMiddleware, secret_key=secret_key)
app.state.limiter = limiter
app.add_middleware(SlowAPIMiddleware)

@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    return JSONResponse(
        status_code=429,
        content={"message": "Too many requests. Please wait a few seconds and try again."}
    )

app.include_router(routers.user.router)
app.include_router(routers.ai.router)
app.include_router(routers.google_auth.router)

@app.get("/", tags=["Root"])
def intro():
    return {"message": "Welcome to the FastAPI application"}
