from fastapi import APIRouter , HTTPException , status , Depends
from sqlalchemy.orm import session
from core.database import get_db

import crud.user

from schemas.user import UserCreate , UserOut

router = APIRouter(prefix="/users", tags=["Users"])

@router.post('/' , response_model=UserOut, response_model_exclude={"hash_password"}, status_code=status.HTTP_201_CREATED)
def create_new_user(user:UserCreate, db: session = Depends(get_db)):

    db_user = crud.user.get_user_by_email(db , email=user.email)
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    return crud.user.create_user(db=db, user=user)

