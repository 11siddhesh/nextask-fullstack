from sqlalchemy import Column, Integer, String, Boolean, DateTime
from src.utils.db import Base


class UserModel(Base):

    __tablename__ = "user_table"
    id = Column(Integer, primary_key=True)
    name = Column(String(20))
    user_name = Column(String(40), nullable=False)
    email = Column(String(100), nullable=False)
    hash_password = Column(String(100), nullable=False)
    mobile_no = Column(String(12))

# --- NEW COLUMNS ---
    is_verified = Column(Boolean, default=False)
    otp = Column(String(6), nullable=True)
    otp_exp = Column(DateTime, nullable=True)