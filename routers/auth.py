from fastapi import APIRouter , Request
from fastapi.responses import RedirectResponse
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
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
async def callback(request: Request, code: str):

    flow = Flow.from_client_config(CLIENT_CONFIG, url)
    flow.redirect_uri = REDIRECT_URI

    try:
        flow.fetch_token(code=code)
        credentials = flow.credentials

        request.session["credentials"] = {
            "token": credentials.token,
            "refresh_token": credentials.refresh_token,
            "token_uri": credentials.token_uri,
            "client_id": credentials.client_id,
            "client_secret": credentials.client_secret,
            "scopes": credentials.scopes
        }
    

        return {"message": "Authentication successful! Token acquired."}
    except Exception:
        return {'Error'}
    


async def get_token_for_user(request: Request):
    session_credentials = request.session.get("credentials")

    if not session_credentials:
        return None

    credentials = Credentials(
        token=session_credentials["token"],
        refresh_token=session_credentials["refresh_token"],
        token_uri=session_credentials["token_uri"],
        client_id=session_credentials["client_id"],
        client_secret=session_credentials["client_secret"],
        scopes=session_credentials["scopes"],
    )

    return credentials