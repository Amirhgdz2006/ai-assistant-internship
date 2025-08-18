from fastapi import Depends , HTTPException , status , Request
from sqlalchemy.orm import Session
from core.database import get_db
from security.jwt_handler import verify_access_token
from crud.user import find_user_by_id
from models.user import User
from core.redis_client import r_client


def get_current_user(request: Request, db: Session = Depends(get_db)):
    session_id = request.cookies.get("session_id")

    if not session_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="No session id found in cookies or you are not logged in")
    
    token = r_client.get(session_id)
    if token is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="No token found from session id")
    
    payload = verify_access_token(token)

    if payload is None or "user_id" not in payload:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Token is expired or invalidated")

    user = find_user_by_id(db, user_id=payload["user_id"])
    if user is not None:
        return user
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="User not found")
