from fastapi import FastAPI
from core.schemas import ChatMessageRequest , ChatMessageResponse
from core.responses import get_responses


app = FastAPI()

@app.get('/')
def message():

    return {"message": "Hello, AI Assistant Developer!"}


@app.get('/items/{item_id}')
def read_item(item_id: int, query:str = None):
    
    return {"item_id":item_id, "query": query}


#-----------------------------------------

@app.post('/chat' , response_model=ChatMessageResponse)
def chat_message(request: ChatMessageRequest):

    user_input = request.message.lower()

    response_data = get_responses()

    if user_input in response_data:
        bot_response = response_data[user_input]
    else:
        bot_response = "Sorry, I didn't understand what you said. Can you rephrase it?"


    return ChatMessageResponse(response=bot_response)


