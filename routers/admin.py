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

@router.get("/get_reservation_by_doctor/{doctor_id}")
async def get_reservations_by_doctor(doctor_id: int, db: db_dependency, user: user_dependency):
    if user.get('role') != RoleEnum.admin:
        raise HTTPException(status_code=403, detail='Only admin can access this resource')
    doctor_reservations = db.query(Reservations).filter(Reservations.doctor_id == doctor_id).all()
    return doctor_reservations

@router.get("/delete_user/{user_id}")
async def delete_user(user_id: int, db: db_dependency, user: user_dependency):
    if user.get('role') != RoleEnum.admin:
        raise HTTPException(status_code=403, detail='Only admin can access to this resource')
    user_to_delete = db.query(Users).filter(Users.id == user_id).first()
    if not user_to_delete:
        raise HTTPException(status_code=404, detail='No users found.')
    db.delete(user_to_delete)
    db.commit()
    
@router.get("/delete_reservation/{reservation_id}")
async def delete_reservation(reservation_id: int, db: db_dependency, user: user_dependency):
    if user.get('role') != RoleEnum.admin:
        raise HTTPException(status_code=403, detail='Only admin can access to this resource')
    user_to_delete = db.query(Reservations).filter(Reservations.id == reservation_id).first()
    if not user_to_delete:
        raise HTTPException(status_code=404, detail='No reservations found.')
    db.delete(user_to_delete)
    db.commit()
    
# changing 'active' column of user to 0
# searching in users
# updating the user roles

@router.put('/block_user/{user_id}')
async def block_user(user_id: int, db: db_dependency, user: user_dependency):
    if user.get('role') != RoleEnum.admin:
        raise HTTPException(status_code=403, detail='Only admin can access to this resource')
    user_to_block = db.query(Users).filter(Users.id == user_id).first()
    if not user_to_block:
        raise HTTPException(status_code=404, detail='No users found.')
    user_to_block.active = False
    db.commit()
    db.refresh(user_to_block)
    return {"message": f"User {user_id} has been blocked."}

@router.get('/search_user/{search_term}')
async def search_user(search_term: str, db: db_dependency, user: user_dependency):
    if user.get('role') != RoleEnum.admin:
        raise HTTPException(status_code=403, detail='Only admin can access to this resource')
    search = f"%{search_term}%"
    users_found = db.query(Users).filter(
        (Users.first_name.ilike(search)) |
        (Users.last_name.ilike(search)) |
        (Users.username.ilike(search)) |
        (Users.email.ilike(search)) |
        (Users.phone_number.ilike(search))
    ).all()
    if not users_found:
        raise HTTPException(status_code=404, detail='No users found.')
    return users_found
@router.get('/search_user/{search_term}')
async def search_user(search_term: str, db: db_dependency, user: user_dependency):
    if user.get('role') != RoleEnum.admin:
        raise HTTPException(status_code=403, detail='Only admin can access to this resource')
    search = f"%{search_term}"
    users_found = db.query(Users).filter(
        (Users.first_name.ilike(search)) |
        (Users.last_name.ilike(search)) |
        (Users.username.ilike(search)) |
        (Users.email.ilike(search)) |
        (Users.phone_number.ilike(search))      
         
    ).all()
    if not users_found:
        raise HTTPException(status_code=404, detail='No users found with the given search term.')


@router.put('/update_user_role/{user_id}')
async def update_user_role(user_id: int, new_role: RoleEnum, db: db_dependency, user: user_dependency):
    if user.get('role') != RoleEnum.admin:
        raise HTTPException(status_code=403, detail='Only admin can access to this resource')
    update_user = db.query(Users).filter(Users.id == user_id).first()
    if not update_user:
        raise HTTPException(status_code=404, detail='No users found with the given ID.')
    update_user.role = new_role
    db.commit()
    db.refresh(update_user)
    return {"message": f"User {user_id} role has been updated to {new_role}."}


@router.put('/update_reservation_status/{reservation_id}')
async def update_reservation_status(reservation_id: int, new_status: str, db: db_dependency, user: user_dependency):
    if user.get('role') != RoleEnum.admin:
        raise HTTPException(status_code=403, detail='Only admin can access to this resource')
    update_reservation_status = db.query(Reservations).filter(Reservations.id == reservation_id).first()
    if not update_reservation_status:
        raise HTTPException(status_code=404, detail='No reservations found with the given ID.')
    update_reservation_status.status = new_status
    db.commit()
    db.refresh(update_reservation_status)
    return {"message": f"Reservation {reservation_id} status has been updated to {new_status}."}