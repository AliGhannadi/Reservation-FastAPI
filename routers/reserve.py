from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from db import SessionLocal
from typing import Annotated, Literal
from schemas import CreateReservation
from models import Reservations
from datetime import datetime, timezone
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

@router.post("/reservations/")
async def create_reserve(db: db_dependency, create_reservation_request: CreateReservation):
    reserve_model = Reservations(
        user_id=create_reservation_request.user_id,
        reservation_time=create_reservation_request.reservation_time
    )
    db.add(reserve_model)
    db.commit()
    db.refresh(reserve_model)
    return reserve_model