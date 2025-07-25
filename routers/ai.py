from fastapi import APIRouter , HTTPException , Request
import openai
from pydantic import BaseModel
from core.config import OPENAI_API_KEY, OPENAI_BASE_URL
from tools import calendar
import json
from routers.auth import get_token_for_user
from datetime import datetime

router = APIRouter(tags=['AI'])

class PromptRequest(BaseModel):
    prompt:str

client = openai.OpenAI(
    api_key=OPENAI_API_KEY,
    base_url=OPENAI_BASE_URL,
)

@router.post('/prompt')
async def run_agent(request:Request , body: PromptRequest):
    if not client.api_key:
        raise HTTPException(status_code=500, detail="API key is not configured.")

    credentials = await get_token_for_user(request)

    tools = [
        {
            "type": "function",
            "function": {
                "name": "list_calendar_events",
                "description": "Lists a specific number of upcoming events from the user's primary Google Calendar.",
                "parameters": {
                "type": "object",
                "properties": {
                    "quantity": {
                    "type": "string",
                    "description": "The number of upcoming calendar events to retrieve. Must be a positive integer as string."
                    }
                },
                "required": ["quantity"]
                }
            }
            },
        
        {
            "type": "function",
            "function": {
                "name": "create_calendar_event",
                "description": "Creates a new event on the user's google calendar.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "title": {"type": "string", "description": "The title of the event."},
                        "start_time": {
                            "type": "string",
                            "description": "The start time in ISO 8601 format.",
                        },
                        "end_time": {
                            "type": "string",
                            "description": "The end time in ISO 8601 format.",
                        },
                        "participants": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "A list of email addresses of the participants.",
                        },
                        "location": {
                        "type": "string",
                        "description": "The physical or virtual location where the event will take place. This can be a meeting room, or a video call format"
                        }
                    },
                    "required": ["title", "start_time", "end_time", "participants"],
                },
            },
        }
    ]

    messages = [{"role": "user", "content": f"today date:{datetime.today().strftime("%Y-%m-%d")}"},{"role": "user", "content": body.prompt}]

    try:

        first_response = openai.chat.completions.create(
            model="gpt-4.1-mini",
            messages=messages,
            tools=tools,
            tool_choice="auto",  
        )

        response_message = first_response.choices[0].message
        tool_calls = response_message.tool_calls

        if not tool_calls:
            return {"response": response_message.content}


  
        messages.append(response_message)
        
        available_functions = {
            "list_calendar_events": calendar.list_calendar_events,
            "create_calendar_event": calendar.create_calendar_event,
        }


        for tool_call in tool_calls:
            function_name = tool_call.function.name
            function_to_call = available_functions[function_name]
            function_args = json.loads(tool_call.function.arguments)
            if function_name in ["list_calendar_events" , "create_calendar_event"]:
                function_args["credentials"] = credentials
            function_response = function_to_call(**function_args)

            messages.append(
            {
                "tool_call_id": tool_call.id,
                "role": "tool",
                "name": function_name,
                "content": function_response,
            }
        )

        
        second_response = openai.chat.completions.create(
            model="gpt-4.1-mini",
            messages=messages,
        )

        return {"response": second_response.choices[0].message.content}

            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))