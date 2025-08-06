from fastapi import APIRouter, HTTPException, Request, status, Depends
from fastapi.responses import JSONResponse
from schemas.user import UserCreate , UserRead, UserUpdate, UserOut
from crud.user import verify_password , create_user , read_existing_user , update_existing_user , delete_existing_user , find_user_by_email ,find_user_by_id
from sqlalchemy.orm import Session
from core.database import get_db
from models.user import User
from security.jwt_handler import create_access_token , verify_access_token
from security.dependencies import require_admin , require_self_or_admin
from core.limiter import limiter

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
            response = JSONResponse(content={"message": "Login successful"})
            response.set_cookie(
                key="access_token",
                value=access_token,
                httponly=True,  
                secure=False, # if you using HTTPS it should be True (secure=True)  
                samesite="lax" 
                )
            return response
        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST , detail="Password mismatch")
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST , detail="Email not found")


# ------------------ Log Out------------------
@router.post("/log_out")
def log_out(request:Request):
    response = JSONResponse(content={"message": "Logged out successfully"})
    response.delete_cookie(key="access_token")
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