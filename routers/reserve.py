from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from db import SessionLocal
from typing import Annotated, Literal
from schemas import CreateAppointmentSlot
from models import Reservations
from datetime import datetime, timezone, timedelta
from .auth import get_current_user 
router = APIRouter(
    prefix='/reserve',
    tags=['reserve']
)
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        
db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]

@router.post("/create_reserve", status_code=201)
async def create_reserve(user: user_dependency, db: db_dependency, create_reservation_request: CreateAppointmentSlot):
    try:
        reserve_model = Reservations(
            user_id=user.get('id'),
            reservation_time=create_reservation_request.reservation_time,
            reason=create_reservation_request.reason,
            number_of_people=1
        )
        db.add(reserve_model)
        db.commit()
        db.refresh(reserve_model)
        return reserve_model
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
@router.get("/my-reservations")
async def get_my_reservations(user: user_dependency, db: db_dependency):
    try:
        reservations = db.query(Reservations).filter(Reservations.user_id == user.get('id')).all()
        return reservations
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))