from fastapi import FastAPI , Request
from fastapi.middleware.cors import CORSMiddleware
from routers import users
from routers import ai
from routers import auth
from starlette.middleware.sessions import SessionMiddleware
import os

from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi.openapi.utils import get_openapi

app = FastAPI(title="AI Assistant API", description="API for an AI-powered chat assistant that manages your calendar.", version="0.1.0")

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

from core.limiter import limiter

origins = ["http://localhost:8000", "http://localhost:3000", "http://localhost:5173"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  
    allow_credentials=True, 
    allow_methods=["*"],    
    allow_headers=["*"]
)

@app.middleware('http')
async def process_time(request: Request, call_next):
    response = await call_next(request)
    return response

app.add_middleware(SessionMiddleware, secret_key=os.getenv("SESSION_SECRET_KEY", "your-super-secret-key"))

app.include_router(users.router)
app.include_router(ai.router)
app.include_router(auth.router, prefix="/auth")

@app.get("/", tags=["Root"])
def read_root():
    return {"message": "Welcome to the AI Assistant API!"}

# ------------------------------ Swagger JWT Support ------------------------------

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )
    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
        }
    }
    for path in openapi_schema["paths"].values():
        for method in path.values():
            method["security"] = [{"BearerAuth": []}]
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi
