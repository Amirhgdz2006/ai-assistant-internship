from fastapi import APIRouter
from fastapi.responses import RedirectResponse
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from core.config import CLIENT_CONFIG

router = APIRouter()

url = ['https://www.googleapis.com/auth/calendar']
REDIRECT_URI = "http://localhost:8000/auth/callback"

@router.get("/login")
async def login():
    flow = Flow.from_client_config(CLIENT_CONFIG, url)
    flow.redirect_uri = REDIRECT_URI

    auth_url, _ = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true',
        prompt='consent'
    )
    return RedirectResponse(auth_url)


@router.get("/callback")
async def callback(code: str):

    flow = Flow.from_client_config(CLIENT_CONFIG, url)
    flow.redirect_uri = REDIRECT_URI

    try:
        flow.fetch_token(code=code)
        credentials = flow.credentials
        build('calendar', 'v3', credentials=credentials)
        return {"message": "Authentication successful! Token acquired."}
    except Exception:
        return {'Error'}