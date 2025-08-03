from sqlalchemy.orm import Session
from passlib.context import CryptContext
from models.user import User
from schemas.user import UserCreate , UserUpdate

password_context = CryptContext(schemes=['bcrypt'] , deprecated='auto')
from utils.jwt_handler import create_access_token

#-------------------------------- create 
def get_hash_password(password):
    return password_context.hash(password)

def get_user_by_email(db:Session , email):
    return db.query(User).filter(User.email==email).first()

def create_user(db:Session , user:UserCreate):
    hashed_password = get_hash_password(user.password)
    db_user = User(email = user.email , hash_password = hashed_password , role = user.role or "user")
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    token = create_access_token({"sub": db_user.email, "user_id": db_user.id})
    return {
        "id": db_user.id,
        "email": db_user.email,
        "is_active": db_user.is_active,
        "role": db_user.role,
        "access_token": token
    }

#-------------------------------- read 
def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(User).offset(skip).limit(limit).all()

def get_user(db: Session, user_id: int):
    return db.query(User).filter(User.id == user_id).first()
#-------------------------------- update
def update_user(db:Session , user_id:int , user_in:UserUpdate):
    db_user = db.query(User).filter(User.id == user_id).first()
    if db_user == None:
        return None

    if user_in.email is not None:
        db_user.email = user_in.email

    if user_in.password is not None:
        db_user.hash_password = get_hash_password(user_in.password)

    if user_in.is_active is not None:
        db_user.is_active = user_in.is_active

    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user
#-------------------------------- delete
def delete_user(db:Session , user_id:int):
    db_user = db.query(User).filter(User.id == user_id).first()
    if db_user == None:
        return None

    db.delete(db_user)
    db.commit()
    return db_user
