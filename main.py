from fastapi import FastAPI

app = FastAPI()

@app.get('/')
def message():
    
    return {"message": "Hello, AI Assistant Developer!"}


@app.get('/items/{item_id}')
def read_item(item_id: int, query:str = None):
    
    return {"item_id":item_id, "query": query}