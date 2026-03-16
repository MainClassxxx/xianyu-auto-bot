"""
用户模型
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from datetime import datetime
from . import ModelBase

class User(ModelBase):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(20), default="user")  # user, admin
    status = Column(String(20), default="active")  # active, inactive, banned
    avatar = Column(String(255), default="")
    agree_terms = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
