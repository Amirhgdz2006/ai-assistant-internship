from fastapi import FastAPI , Request
from fastapi.middleware.cors import CORSMiddleware
from routers import users
from routers import ai
from routers import auth
from starlette.middleware.sessions import SessionMiddleware
import os


app = FastAPI(title="AI Assistant API",description="API for an AI-powered chat assistant that manages your calendar.",version="0.1.0")

origins = ["http://localhost:8000","http://localhost:3000","http://localhost:5173"]

app.add_middleware(
        CORSMiddleware,
    allow_origins=origins,  
    allow_credentials=True, 
    allow_methods=["*"],    
    allow_headers=["*"]
)

@app.middleware('http')
async def process_time(request:Request , call_next):
    response = await call_next(request)
    return response

app.add_middleware(SessionMiddleware, secret_key=os.getenv("SESSION_SECRET_KEY", "your-super-secret-key"))

# app.include_router(chat.router)
app.include_router(users.router)

app.include_router(ai.router)

app.include_router(auth.router , prefix="/auth")

@app.get("/", tags=["Root"])
def read_root():
    return {"message": "Welcome to the AI Assistant API!"}