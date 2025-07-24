import json
from googleapiclient.discovery import build
from datetime import datetime, timezone

def list_calendar_events(quantity:str, credentials):
    if not credentials:
        return json.dumps({"error": "User not authenticated. Please login first."})

    try:
        service = build("calendar", "v3", credentials=credentials)

        events_result = service.events().list(
            calendarId='primary',
            timeMin=datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            maxResults=int(quantity),
            singleEvents=True,
            orderBy='startTime'
        ).execute()

        events = events_result.get('items', [])

        if events == []:
            return 'there is no upcoming events found.'

        simplified_events = []

        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            end = event['end'].get('dateTime', event['end'].get('date'))
            summary = event.get('summary', 'no title')
            temp = {"start":start , "end":end , "summary":summary}
            simplified_events.append(temp)

        return json.dumps(simplified_events)

    except Exception as e:
        return json.dumps({"error": "Failed to fetch calendar events.", "details": str(e)})


def create_calendar_event(title:str , start_time:str , end_time:str , participants:list[str] , credentials):

    if not credentials:
        return json.dumps({"error": "User not authenticated. Please login first."})

    try:
        service = build("calendar", "v3", credentials=credentials)
        event = {
        "summary": title,
        
        "start": {
            "dateTime": start_time,
            "timeZone": "Asia/Tehran"
        },
        "end": {
            "dateTime": end_time,
            "timeZone": "Asia/Tehran"
        },
        "attendees": participants
                }
        service.events().insert(calendarId='primary', body=event).execute()

        return json.dumps(event)

    except Exception as e:
        return json.dumps({"error": "Failed to fetch calendar events.", "details": str(e)})

    

