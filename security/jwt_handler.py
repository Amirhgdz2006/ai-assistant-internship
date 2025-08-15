from jose import jwt , JWTError
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv
import os

load_dotenv()

jwt_secret_key = os.getenv("JWT_SECRET_KEY")
algorithm = "HS256"
access_token_expire_time = 10

refresh_token_expire_time = 24 * 60

# ---------- access token ----------

def create_access_token(data:dict):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=access_token_expire_time)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, jwt_secret_key, algorithm=algorithm)

    return encoded_jwt

def verify_access_token(token):
    try:
        payload = jwt.decode(token, jwt_secret_key, algorithms=[algorithm])
        return payload
    except JWTError:
        return None
