from fastapi import APIRouter , HTTPException
import openai
from pydantic import BaseModel
from core.config import OPENAI_API_KEY, OPENAI_BASE_URL

router = APIRouter(tags=['AI'])

class PromptRequest(BaseModel):
    prompt:str

client = openai.OpenAI(
    api_key=OPENAI_API_KEY,
    base_url=OPENAI_BASE_URL,
)

@router.post('/prompt')
async def generate_response(request: PromptRequest):
    if not client.api_key:
        raise HTTPException(status_code=500, detail="API key is not configured.")

    try:
        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": request.prompt}
            ],
            max_tokens=150
        )
        return {"response": response.choices[0].message.content.strip()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))