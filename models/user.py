from core.database import Base
from sqlalchemy import Column, Integer, String , Boolean

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True ,nullable=False)
    password = Column(String, nullable=True)
    role = Column(String, default='user')
    is_active = Column(Boolean, default=True)
    auth_with_google = Column(Boolean , default=False)