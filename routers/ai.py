from fastapi import APIRouter , HTTPException
import openai
from pydantic import BaseModel
from core.config import OPENAI_API_KEY, OPENAI_BASE_URL
from tools import weather
import json

router = APIRouter(tags=['AI'])

class PromptRequest(BaseModel):
    prompt:str

client = openai.OpenAI(
    api_key=OPENAI_API_KEY,
    base_url=OPENAI_BASE_URL,
)

@router.post('/prompt')
async def run_agent(request: PromptRequest):
    if not client.api_key:
        raise HTTPException(status_code=500, detail="API key is not configured.")


    tools = [
        {
            "type": "function",
            "function": {
                "name": "get_current_weather",
                "description": "Get the current weather in a given location",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "location": {
                            "type": "string",
                            "description": "The city and state, e.g. San Francisco, CA",
                        },
                        "unit": {"type": "string", "enum": ["celsius", "fahrenheit"]},
                    },
                    "required": ["location"],
                },
            },
        }
    ]

    messages = [{"role": "user", "content": request.prompt}]

    try:

        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=messages,
            tools=tools,
            tool_choice="auto",  
        )

        response_message = response.choices[0].message
        tool_calls = response_message.tool_calls


        if tool_calls:
  
            available_functions = {
                "get_current_weather": weather.get_current_weather,
            }


            tool_call = tool_calls[0]
            function_name = tool_call.function.name
            function_to_call = available_functions[function_name]
            function_args = json.loads(tool_call.function.arguments)

            function_response = function_to_call(**function_args)

            return {
                "model_decision": f"Calling function: {function_name} with args: {function_args}",
                "function_result": json.loads(function_response)
            }
        else:
            return {"response": response_message.content}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))