from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from db import SessionLocal
from typing import Annotated, List
from schemas import CreateReservation
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
    appointment: CreateReservation,
    db: db_dependency
):
    """Doctors can create available appointment slots"""
    if user.get('role') != RoleEnum.doctor:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Only doctors can create appointment slots'
        )
    
    # Create an available appointment slot
    new_slot = Reservations(
        reservation_time=appointment.reservation_time,
        reason="Available for booking",
        status="available",
        doctor_id=user.get('id')  # The doctor creating the slot
    )
    
    db.add(new_slot)
    db.commit()
    db.refresh(new_slot)
    return new_slot

@router.get("/available")
async def get_available_appointments(
    db: db_dependency
):
    """Get all available appointment slots"""
    available = db.query(Reservations).filter(
        Reservations.status == "available"
    ).order_by(Reservations.reservation_time).all()
    
    # Get doctor information for each slot
    result = []
    for slot in available:
        doctor = db.query(Users).filter(Users.id == slot.doctor_id).first()
        result.append({
            "id": slot.id,
            "doctor_name": f"Dr. {doctor.first_name} {doctor.last_name}",
            "time": slot.reservation_time,
            "status": slot.status
        })
    return result

@router.post("/book/{slot_id}", status_code=status.HTTP_201_CREATED)
async def book_appointment(
    slot_id: int,
    user: user_dependency,
    db: db_dependency
):
    """Users can book available appointment slots"""
    if user.get('role') not in [RoleEnum.user, RoleEnum.admin]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Only patients can book appointments'
        )
    
    # Check if slot exists and is available
    slot = db.query(Reservations).filter(
        Reservations.id == slot_id,
        Reservations.status == "available"
    ).first()
    
    if not slot:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Appointment slot not found or already booked"
        )
    
    # Update the slot with patient's information
    slot.status = "booked"
    slot.user_id = user.get('id')  # Set the patient's ID
    slot.reason = f"Appointment booked by patient {user.get('id')}"
    db.commit()
    db.refresh(slot)
    return slot

@router.get("/doctor/my-schedule")
async def get_doctor_schedule(
    user: user_dependency,
    db: db_dependency
):
    """Doctors can view their appointment schedule"""
    if user.get('role') != RoleEnum.doctor:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Only doctors can view their schedule'
        )
    
    appointments = db.query(Reservations).filter(
        Reservations.doctor_id == user.get('id')
    ).order_by(Reservations.reservation_time).all()
    
    return appointments

@router.get("/my-appointments")
async def get_my_appointments(
    user: user_dependency,
    db: db_dependency
):
    """Users can view their booked appointments"""
    appointments = db.query(Reservations).filter(
        Reservations.status == "booked",
        Reservations.reason.like(f"%patient {user.get('id')}%")
    ).order_by(Reservations.reservation_time).all()
    
    # Get doctor information for each appointment
    result = []
    for apt in appointments:
        doctor = db.query(Users).filter(Users.id == apt.user_id).first()
        result.append({
            "id": apt.id,
            "doctor_name": f"Dr. {doctor.first_name} {doctor.last_name}",
            "time": apt.reservation_time,
            "status": apt.status
        })
    return result