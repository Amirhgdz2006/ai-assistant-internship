from pydantic import BaseModel , EmailStr
from typing import Optional

class UserCreate(BaseModel):
    email : EmailStr
    password : str


class UserOut(BaseModel):
    id : int
    email : EmailStr
    is_active : bool

    class Config():
        orm_mode = True

class UserUpdate(BaseModel):
    email : Optional[EmailStr] = None
    password : Optional[str] = None
    is_active : Optional[bool] = None

    