from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from db import SessionLocal
from typing import Annotated, List
from schemas import CreateAppointmentSlot
from models import Users, Reservations, RoleEnum
from datetime import datetime, timezone, timedelta
from .auth import get_current_user 

router = APIRouter(
    prefix='/appointments',
    tags=['appointments']
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        
db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]

@router.post("/doctor/create-slot", status_code=status.HTTP_201_CREATED)
async def create_appointment_slot(
    user: user_dependency,
    appointment: CreateAppointmentSlot,
    db: db_dependency
):
    """Doctors can create available appointment slots"""
    if user.get('role') not in [RoleEnum.doctor, RoleEnum.admin]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Only doctors can create appointment slots'
        )
    
    # Create an available appointment slot
    new_slot = Reservations(
        reservation_time=appointment.reservation_time,
        description=appointment.description,
        status="available",
        doctor_id=user.get('id')  # The doctor creating the slot
    )
    
    db.add(new_slot)
    db.commit()
    db.refresh(new_slot)
    return new_slot

@router.get("/doctor/my-schedule")
async def get_doctor_schedule(
    user: user_dependency,
    db: db_dependency
):
    """Doctors can view their appointment schedule"""
    if user.get('role') not in [RoleEnum.doctor, RoleEnum.admin]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Only doctors can view their schedule'
        )
    
    appointments = db.query(Reservations).filter(
        Reservations.doctor_id == user.get('id')
    ).order_by(Reservations.reservation_time).all()
    
    return appointments

@router.put("/doctor/cancel-slot/{slot_id}")
async def cancel_appointment_slot(
    slot_id: int,
    user: user_dependency,
    db: db_dependency
):
    """Doctors can cancel their appointment slots"""
    if user.get('role') not in [RoleEnum.doctor, RoleEnum.admin]:
       raise HTTPException(status_code=403, detail='Only doctors can cancel appointment slots')
    cancel_slot = db.query(Reservations).filter(Reservations.id == slot_id, Reservations.doctor_id == user.get('id')).first()
    if not cancel_slot:
        raise HTTPException(status_code=404, detail='Appointment slot not found or you are not authorized to cancel it')
    cancel_slot.update({'status': 'canceled'})
    db.commit()
    return {"message": "Appointment slot canceled successfully"}
    