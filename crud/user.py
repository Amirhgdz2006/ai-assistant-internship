from sqlalchemy.orm import Session
from schemas.user import UserCreate , UserCreateGoogle , UserOut, UserUpdate
from models.user import User
from passlib.context import CryptContext

password_context = CryptContext(schemes=['bcrypt'] , deprecated='auto')

# ----------- password (passlib) ----------- 

def hash_password(password):
    return password_context.hash(password)

def verify_password(password , hashed_password):
    return password_context.verify(password , hashed_password)

# ----------- finding user -----------

def find_user_by_email(db:Session , user_email:str):
    user = db.query(User).filter(User.email == user_email).first()
    return user

def find_user_by_id(db:Session , user_id:int):
    user = db.query(User).filter(User.id == user_id).first()
    return user

# ----------- create user -----------
def create_user(db:Session , user_data:UserCreateGoogle):
    user = db.query(User).filter(User.email == user_data.email).first()
    if user is None:
        if user_data.password != None:
            new_user = User(email=user_data.email,password=hash_password(user_data.password),role=user_data.role)
            db.add(new_user)
            db.commit()
            db.refresh(new_user)
        else:
            new_user = User(email=user_data.email,password=None,role=user_data.role,auth_with_google=True)
            db.add(new_user)
            db.commit()
            db.refresh(new_user)
        return new_user
    return user

# ----------- read existing user -----------
def read_existing_user(db:Session , user_id:int):
    user = db.query(User).filter(User.id == user_id).first()
    if user is not None:
        return {
            "id" : user.id,
            "email" : user.email,
            "password" : user.password,
            "role" : user.role,
            "is_active" : user.is_active
        }


# ----------- update existing user -----------
def update_existing_user(db:Session , user_id:int , user_data:UserUpdate):
    user = db.query(User).filter(User.id == user_id).first()
    if user is not None:
        user.email = user_data.email
        user.password = hash_password(user_data.password)
        user.is_active = user_data.is_active
        db.commit()
        db.refresh(user)
        return {
            "id" : user.id,
            "email" : user.email,
            "password" : user.password,
            "role" : user.role,
            "is_active" : user.is_active
        }

    
# ----------- delete existing user -----------
def delete_existing_user(db:Session , user_id:int):
    user = db.query(User).filter(User.id == user_id).first()
    if user is not None:
        db.delete(user)
        db.commit()
        return {"user deleted"}

