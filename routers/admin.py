from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Annotated, List
from db import SessionLocal
from .auth import get_current_user, bcrypt_context, get_db
from models import Users, Reservations, RoleEnum
from datetime import datetime, timezone, timedelta

router = APIRouter(
    prefix="/admin",
    tags=["admin"],)
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        
db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]
@router.get("/test")
async def admin_test():
    return {"message": "Admin route is working!"}

@router.get("/get_all_users")
async def get_all_users(db: db_dependency, user: user_dependency):
    if user.get('role') != RoleEnum.admin:
        raise HTTPException(status_code=403, detail='Only admins can access this resource')
    all_users = db.query(Users).all()
    return all_users


@router.get("/get_all_reservations")
async def get_all_reservations(db: db_dependency, user: user_dependency):
    if user.get('role') != RoleEnum.admin:
        raise HTTPException(status_code=403, detail='Only admin can access this resource')
    all_reservations = db.query(Reservations).all()
    return all_reservations

@router.get("/get_reservations_by_user/{user_id}")
async def get_reservations_by_user(user_id: int, db: db_dependency, user: user_dependency):
    if RoleEnum.admin not in user.get('role'):
        raise HTTPException(status_code=403, detail='Only admin can access this resource')
    user_reservations = db.query(Reservations).filter(Reservations.user_id == user_id).all()
    return user_reservations
    
    