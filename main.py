from fastapi import FastAPI
from core.schemas import ChatMessageRequest , ChatMessageResponse
from core.responses import get_responses
from core.api.endpoints import router

app = FastAPI()

@app.get('/')
def message():

    return {"message": "Hello, AI Assistant Developer!"}


app.include_router(router,prefix='/api/v1')