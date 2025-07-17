from sqlalchemy.orm import Session
from passlib.context import CryptContext
from models.user import User
from schemas.user import UserCreate , UserUpdate

password_context = CryptContext(schemes=['bcrypt'] , deprecated='auto')

#-------------------------------- create 
def get_hash_password(password):
    return password_context.hash(password)

def get_user_by_email(db:Session , email):
    return db.query(User).filter(User.email==email).first()

def create_user(db:Session , user:UserCreate):
    hashed_password = get_hash_password(user.password)
    db_user = User(email = user.email , hash_password = hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user
#-------------------------------- read 
def get_user(db: Session, user_id: int):
    return db.query(User).filter(User.id == user_id).first()
#-------------------------------- update
def update_user(db:Session , user_id:int , user_in:UserUpdate):
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        return None
    
    update_data = user_in.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_user, key, value)

    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user
#-------------------------------- delete
def delete_user(db:Session , user_id:int):
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        return None

    db.delete(db_user)
    db.commit()
    return db_user

