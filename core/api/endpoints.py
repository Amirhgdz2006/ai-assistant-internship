from fastapi import FastAPI , APIRouter , HTTPException
from core.responses import get_responses
from core.schemas import ChatMessageRequest , ChatMessageResponse

router = APIRouter()

@router.post('/chat' , response_model=ChatMessageResponse)
def chat_message(request:ChatMessageRequest):
    
    user_input = request.message.lower()

    if user_input == 'Error':
        raise HTTPException(status_code=400, detail='This is a test message.')

    response_data = get_responses()

    if user_input in response_data:
        bot_response = response_data[user_input]
    else:
        bot_response = "Sorry, I didn't understand what you said. Can you rephrase it?"

    return ChatMessageResponse(response=bot_response)