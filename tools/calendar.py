import json
from datetime import datetime

def list_calendar_events(start_time:str , end_time:str):

    mock_events = [
        {"title": "Project Stand-up", "start": "2023-10-27T09:00:00", "end": "2023-10-27T09:30:00"},
        {"title": "Code Review", "start": "2023-10-27T14:00:00", "end": "2023-10-27T15:00:00"},
    ]

    print(f"Searching for events between {start_time} and {end_time}...")

    return json.dumps(mock_events)


def create_calendar_event(title:str , start_time:str , end_time:str , participants:list[str]):

    response = {
        "status": "success",
        "event_details": {
            "title": title,
            "start_time": start_time,
            "end_time": end_time,
            "participants": participants
        }
    }

    print(f"Event '{title}' created from {start_time} to {end_time} with {', '.join(participants)}.")

    return json.dumps(response)
