from fastapi import FastAPI , Request
from core.api.endpoints import router

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title='AI Assistant API')

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

@app.get('/')
def message():

    return {"message": "Hello, AI Assistant Developer!"}

app.include_router(router,prefix='/api/v1')


