from fastapi import APIRouter , Request , status  , Depends
from fastapi.responses import RedirectResponse, JSONResponse
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from core.config import CLIENT_CONFIG
from schemas.user import UserCreateGoogle
from sqlalchemy.orm import Session
from core.database import get_db
from crud.user import find_user_by_email , create_user
from security.jwt_handler import create_access_token
import json

router = APIRouter(tags=["Google-Auth"])

url = [
    'https://www.googleapis.com/auth/calendar',
    'https://www.googleapis.com/auth/userinfo.email',
    'https://www.googleapis.com/auth/userinfo.profile',
    'openid'
]

REDIRECT_URI = "http://localhost:8000/callback"

@router.get("/google_auth")
async def google_auth():
    flow = Flow.from_client_config(CLIENT_CONFIG, url)
    flow.redirect_uri = REDIRECT_URI

    auth_url, _ = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true',
        prompt='consent'
    )
    return RedirectResponse(auth_url)



@router.get("/callback")
async def callback(request: Request, code: str, db: Session = Depends(get_db)):

    flow = Flow.from_client_config(CLIENT_CONFIG, url)
    flow.redirect_uri = REDIRECT_URI

    try:
        flow.fetch_token(code=code)
        credentials = flow.credentials

        oauth2_service = build('oauth2', 'v2', credentials=credentials)
        user_data = oauth2_service.userinfo().get().execute()
        email = user_data['email']
        user = find_user_by_email(db, user_email=email)

        if user is None:
            user_info = UserCreateGoogle(email=email , auth_with_google=True)
            user = create_user(db, user_data=user_info)

        access_token = create_access_token({"user_id": user.id})
        response = RedirectResponse(url="http://localhost:8000/docs", status_code=status.HTTP_302_FOUND)
        response.set_cookie(
            key="access_token",
            value=access_token,
            httponly=True,
            samesite="lax",
            secure=False # if you using HTTPS it should be True (secure=True)
        )

        response.set_cookie(
            key="credentials",
            value=json.dumps({
                "token": credentials.token,
                "refresh_token": credentials.refresh_token,
                "token_uri": credentials.token_uri,
                "client_id": credentials.client_id,
                "client_secret": credentials.client_secret,
                "scopes": credentials.scopes,
            }),
            httponly=True,
            samesite="lax",
            secure=False,  # if you using HTTPS it should be True (secure=True)
            max_age=3600  
        )

        return response
    
    except Exception as e:
        return JSONResponse(status_code=400, content={"error": str(e)})



async def get_token_for_user(request: Request):
    session_credentials = request.cookies.get("credentials")

    if not session_credentials:
        return None

    session_credentials = json.loads(session_credentials)

    credentials = Credentials(
        token=session_credentials["token"],
        refresh_token=session_credentials["refresh_token"],
        token_uri=session_credentials["token_uri"],
        client_id=session_credentials["client_id"],
        client_secret=session_credentials["client_secret"],
        scopes=session_credentials["scopes"],
    )

    return credentials
