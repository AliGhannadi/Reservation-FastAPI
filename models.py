from db import Base
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime


class Users(Base):
    __tablename__= 'users'
    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    username = Column(String, unique=True, nullable=False)
    hashed_password = Column(String)
    phone_number = Column(String, unique=True, nullable=False)
    admin = Column(Boolean, default=False)
    appointments = Column(String, nullable=True)  # New column added

class Reservations(Base):
    __tablename__ = 'reservations'
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    reservation_time = Column(DateTime)
    number_of_people = Column(Integer)
