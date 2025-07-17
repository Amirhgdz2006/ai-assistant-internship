from fastapi import APIRouter , HTTPException , status , Depends
from sqlalchemy.orm import Session
from core.database import get_db
from typing import Optional , List
import crud.user

from schemas.user import UserCreate , UserOut , UserUpdate

router = APIRouter(prefix="/users", tags=["Users"])

@router.post('/' , response_model=UserOut, status_code=status.HTTP_201_CREATED)
def create_new_user(user:UserCreate, db: Session = Depends(get_db)):

    db_user = crud.user.get_user_by_email(db , email=user.email)
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    return crud.user.create_user(db=db, user=user)

@router.get("/", response_model=List[UserOut])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    users = crud.user.get_users(db, skip=skip, limit=limit)
    return users

@router.get("/{user_id}", response_model=UserOut)
def read_user(user_id: int, db: Session = Depends(get_db)):
    db_user = crud.user.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

@router.put("/{user_id}", response_model=UserOut)
def update_existing_user(user_id: int, user_in: UserUpdate, db: Session = Depends(get_db)):
    updated_user = crud.user.update_user(db, user_id=user_id, user_in=user_in)
    if updated_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return updated_user

@router.delete("/{user_id}", response_model=UserOut)
def delete_existing_user(user_id: int, db: Session = Depends(get_db)):
    deleted_user = crud.user.delete_user(db, user_id=user_id)
    if deleted_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return deleted_user