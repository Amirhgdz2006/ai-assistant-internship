from fastapi import APIRouter , Request , Depends, HTTPException, status
from fastapi.responses import RedirectResponse
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from core.config import CLIENT_CONFIG

from schemas.user import UserCreate

from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from core.database import get_db
from crud.user import get_user_by_email , create_user
from passlib.context import CryptContext
from utils.jwt_handler import create_access_token

router = APIRouter(tags=["Auth"])

url = ['https://www.googleapis.com/auth/calendar',
    'https://www.googleapis.com/auth/userinfo.email',
    'https://www.googleapis.com/auth/userinfo.profile',
    'openid']

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
async def callback(request: Request, code: str, db: Session = Depends(get_db)):

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

        #---------------------
        oauth2_service = build('oauth2', 'v2', credentials=credentials)
        user_info = oauth2_service.userinfo().get().execute()
        email = user_info['email']
        


        user = get_user_by_email(db, email=email)
        if not user:
            user_in = UserCreate(email=email, password="google-oauth")
            user = create_user(db, user=user_in)

        access_token = create_access_token({"user_id": user.id})

        return {
            "message": "Google login successful",
            "access_token": access_token,
            "token_type": "bearer",
        }
        #---------------------
    
    except Exception as e:
        return {"error": str(e)}
    


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

# -----------------------------

