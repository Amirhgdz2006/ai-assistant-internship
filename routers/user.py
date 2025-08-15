from fastapi import APIRouter, HTTPException, Request, status,Response, Depends
from fastapi.responses import JSONResponse
from schemas.user import UserCreate , UserRead, UserUpdate, UserOut
from crud.user import verify_password , create_user , read_existing_user , update_existing_user , delete_existing_user , find_user_by_email ,find_user_by_id
from sqlalchemy.orm import Session
from core.database import get_db
from models.user import User
from security.jwt_handler import create_access_token,  verify_access_token
from core.limiter import limiter
from core.redis_client import r_client
import uuid

router = APIRouter(prefix='/user' , tags=['User'])


# ------------------ Sign Up ------------------
@router.post("/sign_up", response_model=UserOut)
@limiter.limit("1/10 second")
def sign_up(user_data:UserCreate , request:Request , db:Session = Depends(get_db)):
    user = find_user_by_email(db , user_email = user_data.email)

    if user is not None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
    
    else:
        return create_user(db , user_data = user_data)


# ------------------ Log In ------------------
@router.post("/log_in")
def log_in(user_data:UserRead , request:Request , db:Session = Depends(get_db)):
    user = find_user_by_email(db , user_email = user_data.email)

    if user is not None:
        if verify_password(user_data.password , user.password):
            access_token = create_access_token({"user_id":user.id})
            # refresh_token = create_refresh_token({"user_id":user.id})

            response = JSONResponse(content={"message": "Login successful"})
            session_id = str(uuid.uuid4())
            response.set_cookie(
                key="session_id",
                value=session_id,
                httponly=True,  
                secure=False, # if you using HTTPS it should be True (secure=True)  
                samesite="lax" 
                )
            
            r_client.set(session_id,access_token)
            
            # response.set_cookie(
            #     key="refresh_token",
            #     value=refresh_token,
            #     httponly=True,
            #     secure=False, # if you using HTTPS it should be True (secure=True)  
            #     samesite="lax" 
            # )

            return response
        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST , detail="Email not found or Password mismatch")
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST , detail="Email not found or Password mismatch")


# ------------------ Log Out ------------------
@router.post("/log_out")
def log_out(response:Response , request:Request):
    session_id = request.cookies.get("session_id")

    if session_id is not None:
        response.delete_cookie("session_id")

        return JSONResponse(content={"message": "Logged out successfully"})
    else:
        return JSONResponse(content={"message": "No user is currently logged in"})
    
    
# ------------------ Read User ------------------
@router.get("/read_userd", response_model=UserOut)
@limiter.limit("1/10 second")
def read_user(request:Request, db:Session = Depends(get_db)):
    session_id = request.cookies.get("session_id")
    if not session_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="No session id found in cookies or you are not logged in")
    
    token = r_client.get(session_id)
    if token is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="No token found from session id")
    
    payload = verify_access_token(token)
    if payload is None or "user_id" not in payload:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="Token is expired or invalidated")

    user = find_user_by_id(db, user_id=payload["user_id"])
    if user is not None:
        return user

    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST , detail="user not found")


# ------------------ Update User ------------------
@router.put("/update_user", response_model=UserOut)
@limiter.limit("1/10 second")
def update_user(user_data:UserUpdate , request:Request , db:Session = Depends(get_db)):
    session_id = request.cookies.get("session_id")
    if not session_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="No session id found in cookies or you are not logged in")
    
    token = r_client.get(session_id)
    if token is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="No token found from session id")
    
    payload = verify_access_token(token)
    if payload is None or "user_id" not in payload:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="Token is expired or invalidated")

    user = find_user_by_id(db, user_id=payload["user_id"])

    if user is not None:
        return update_existing_user(db , user_id=user.id , user_data=user_data)
        
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST , detail="user not found")


# ------------------ Delete User ------------------
@router.delete("/delete_user")
@limiter.limit("1/10 second")
def delete_user(request:Request , db:Session = Depends(get_db)):
    session_id = request.cookies.get("session_id")
    if not session_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="No session id found in cookies or you are not logged in")
    
    token = r_client.get(session_id)
    if token is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="No token found from session id")
    
    payload = verify_access_token(token)
    if payload is None or "user_id" not in payload:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="Token is expired or invalidated")

    user = find_user_by_id(db, user_id=payload["user_id"])

    if user is not None:
        if user.role == "admin":
            return delete_existing_user(db , user_id=user.id)
        else:
            return HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="Admin access required")
    
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST , detail="user not found")