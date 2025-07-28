from sqlalchemy import  Column , String , Integer , VARCHAR , Boolean
from core.database import Base

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer , index=True , primary_key=True)
    email = Column(String , unique=True , index=True , nullable=False)
    hash_password = Column(String , nullable=False)
    is_active = Column(Boolean , default=True)
    # ------------------------------
    role = Column(String, default="user")
    # ------------------------------