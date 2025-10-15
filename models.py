from db import Base
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime
from datetime import datetime, timezone
from typing import Literal
from enum import Enum
from sqlalchemy import Enum as SQLEnum

class RoleEnum(str, Enum):
    user = 'user'
    doctor = 'doctor'
    admin = 'admin'
class Users(Base):
    __tablename__= 'users'
    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    username = Column(String, unique=True, nullable=False)
    hashed_password = Column(String)
    phone_number = Column(String, unique=True, nullable=False)
    active = Column(Boolean, default=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    role = Column(SQLEnum(RoleEnum), default=RoleEnum.user, nullable=False)
    appointments = Column(String, nullable=True)  # New column added

class Reservations(Base):
    __tablename__ = 'reservations'
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # Patient ID when booked
    doctor_id = Column(Integer, ForeignKey("users.id"), nullable=False)  # Doctor who created the slot
    reservation_time = Column(DateTime)
    description = Column(String, nullable=False)
    status = Column(String, default='available')  # available, booked, cancelled
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, nullable=True, onupdate=lambda: datetime.now(timezone.utc))

