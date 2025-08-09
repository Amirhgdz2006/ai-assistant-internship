from fastapi import APIRouter, HTTPException, Request, status, Depends
from fastapi.responses import JSONResponse
from schemas.user import UserCreate , UserRead, UserUpdate, UserOut
from crud.user import verify_password , create_user , read_existing_user , update_existing_user , delete_existing_user , find_user_by_email ,find_user_by_id
from sqlalchemy.orm import Session
from core.database import get_db
from models.user import User
from security.jwt_handler import create_access_token , create_refresh_token ,  verify_access_token
from security.dependencies import require_admin , require_self_or_admin
from core.limiter import limiter
from core.redis_client import r_client

router = APIRouter(prefix='/user' , tags=['User'])


# ------------------ Sign In ------------------
@router.post("/sign_in", response_model=UserOut)
@limiter.limit("1/10 second")
def sign_in(user_data:UserCreate , request:Request , db:Session = Depends(get_db)):
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
            refresh_token = create_refresh_token({"user_id":user.id})

            response = JSONResponse(content={"message": "Login successful"})

            response.set_cookie(
                key="access_token",
                value=access_token,
                httponly=True,  
                secure=False, # if you using HTTPS it should be True (secure=True)  
                samesite="lax" 
                )
            
            response.set_cookie(
                key="refresh_token",
                value=refresh_token,
                httponly=True,
                secure=False, # if you using HTTPS it should be True (secure=True)  
                samesite="lax" 
            )

            return response
        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST , detail="Password mismatch")
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST , detail="Email not found")


# ------------------ Log Out ------------------
@router.post("/log_out")
def log_out(request:Request):
    user_token = request.cookies.get("access_token")
    if user_token:
        payload = verify_access_token(user_token)
        if payload and "user_id" in payload:
            user_id = payload["user_id"]
            r_client.delete(f"user_id:{user_id}")
            r_client.delete(f"refresh_token:{user_id}")

    response = JSONResponse(content={"message": "Logged out successfully"})
    response.delete_cookie(key="access_token")
    response.delete_cookie(key="refresh_token")
    return response

# ------------------ Refresh Token ------------------
@router.post("/refresh_token")
def refresh_token(request: Request):
    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token:
        raise HTTPException(status_code=401, detail="No refresh token provided")

    payload = verify_access_token(refresh_token)  # چون ساختار JWT مشابه است از همین فانکشن استفاده کن

    if payload is None or "user_id" not in payload:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    user_id = payload["user_id"]
    saved_refresh_token = r_client.get(f"refresh_token:{user_id}")

    if saved_refresh_token != refresh_token:
        raise HTTPException(status_code=401, detail="Refresh token is revoked or invalid")

    new_access_token = create_access_token({"user_id": user_id})

    response = JSONResponse(content={"message": "Access token refreshed"})

    response.set_cookie(
        key="access_token",
        value=new_access_token,
        httponly=True,
        secure=False, # if you using HTTPS it should be True (secure=True) 
        samesite="lax"
    )

    return response

# ------------------ Read User ------------------
@router.get("/read_user/{user_id}", response_model=UserOut)
@limiter.limit("1/10 second")
def read_user(user_id:int, request:Request, db:Session = Depends(get_db), _: User = Depends(require_self_or_admin)):
    user = find_user_by_id(db , user_id = user_id)
    
    if user is not None:
        return user
    
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST , detail="user not found")


# ------------------ Update User ------------------
@router.put("/update_user/{user_id}")
@limiter.limit("1/10 second")
def update_user(user_id:int , user_data:UserUpdate , request:Request , db:Session = Depends(get_db), _: User = Depends(require_self_or_admin)):
    user = find_user_by_id(db , user_id=user_id)

    if user is not None:
        return update_existing_user(db , user_id=user_id , user_data=user_data)
        
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST , detail="user not found")


# ------------------ Delete User ------------------
@router.delete("/delete_user/{user_id}")
@limiter.limit("1/10 second")
def delete_user(user_id:int , request:Request , db:Session = Depends(get_db), _: User = Depends(require_admin)):
    user = find_user_by_id(db , user_id=user_id)

    if user is not None:
        return delete_existing_user(db , user_id=user_id)
    
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST , detail="user not found")