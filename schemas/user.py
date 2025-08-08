from pydantic import BaseModel , EmailStr
from typing import Optional


class UserCreate(BaseModel):
    email : EmailStr
    password : str
    role : Optional[str] = 'user'


class UserCreateGoogle(BaseModel):
    email : EmailStr
    password : Optional[str] = None
    role : Optional[str] = 'user'
    auth_with_google : Optional[bool] = True

class UserRead(BaseModel):
    email : EmailStr
    password : str

class UserUpdate(BaseModel):
    email : EmailStr
    password : str
    is_active : bool

class UserOut(BaseModel):
    id : int
    email : EmailStr
    role : str
    is_active : bool

    class Config():
        from_attributes = True