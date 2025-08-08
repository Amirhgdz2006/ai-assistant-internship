from fastapi import Depends , HTTPException , status , Request
from sqlalchemy.orm import Session
from core.database import get_db
from security.jwt_handler import verify_access_token
from crud.user import find_user_by_id
from models.user import User
from core.redis_client import r_client


def get_current_user(request: Request, db: Session = Depends(get_db)):
    token = request.cookies.get("access_token")

    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="No token found in cookies or you are not logged in")

    payload = verify_access_token(token)

    if payload is None or "user_id" not in payload:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="Token is expired or invalidated")

    saved_token = r_client.get(f"user_id:{payload["user_id"]}")

    if saved_token != token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Token is expired or invalidated")

    user = find_user_by_id(db, user_id=payload["user_id"])
    if user is not None:
        return user
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="User not found")

# ---------- requirements ----------

def require_admin(current_user: User = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return current_user

def require_self_or_admin(user_id: int, current_user: User = Depends(get_current_user)):
    if current_user.role != "admin" and current_user.id != user_id:
        raise HTTPException(status_code=403, detail="You don't have access")
    return current_user
