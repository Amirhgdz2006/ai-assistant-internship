from sqlalchemy.orm import session
from passlib.context import CryptContext
from models.user import User
from schemas.user import UserCreate

password_context = CryptContext(schemes=['bcrypt'] , deprecated='auto')


def get_hash_password(password):
    return password_context.hash(password)

def get_user_by_email(db:session , email):
    return db.query(User).filter(User.email==email).first()

def create_user(db:session , user:UserCreate):
    hashed_password = get_hash_password(user.password)
    db_user = User(email = user.email , hash_password = hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

