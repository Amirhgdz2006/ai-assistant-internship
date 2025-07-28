from fastapi import APIRouter , HTTPException , status , Request , Depends
from sqlalchemy.orm import Session
from core.database import get_db
from typing import Optional , List
import crud.user

from schemas.user import UserCreate , UserOut , UserUpdate

# ------------------------------
from core.limiter import limiter  
# ------------------------------
from utils.dependencies import require_admin , require_self_or_admin
from models.user import User
# ------------------------------

router = APIRouter(prefix="/users", tags=["Users"])


@router.post('/' , response_model=UserOut, status_code=status.HTTP_201_CREATED)
@limiter.limit("1/minute")
def create_new_user(user: UserCreate, request: Request, db: Session = Depends(get_db)):
    db_user = crud.user.get_user_by_email(db , email=user.email)
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    return crud.user.create_user(db=db, user=user)


@router.get("/", response_model=List[UserOut])
@limiter.limit("1/minute")
def read_users(request: Request, skip: int = 0, limit: int = 100, db: Session = Depends(get_db), _: User = Depends(require_admin)):
    users = crud.user.get_users(db, skip=skip, limit=limit)
    return users


@router.get("/{user_id}", response_model=UserOut)
@limiter.limit("1/minute")
def read_user(user_id: int, request: Request, db: Session = Depends(get_db), _: User = Depends(require_self_or_admin)):
    db_user = crud.user.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


@router.put("/{user_id}", response_model=UserOut)
@limiter.limit("1/minute")
def update_existing_user(user_id: int, request: Request, user_in: UserUpdate, db: Session = Depends(get_db), _: User = Depends(require_self_or_admin)):
    updated_user = crud.user.update_user(db, user_id=user_id, user_in=user_in)
    if updated_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return updated_user


@router.delete("/{user_id}", response_model=UserOut)
@limiter.limit("1/minute")
def delete_existing_user(user_id: int, request: Request, db: Session = Depends(get_db), _: User = Depends(require_admin)):
    deleted_user = crud.user.delete_user(db, user_id=user_id)
    if deleted_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return deleted_user
