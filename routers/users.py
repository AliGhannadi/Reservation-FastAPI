from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from db import SessionLocal
from typing import Annotated, Literal
from schemas import CreateUser
from models import Users
from passlib.context import CryptContext

# Password hashing configuration
bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

router = APIRouter(
    prefix='/users',
    tags=['users']
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]

@router.get("/")
async def get_users():
    return {"message": "Users route is working!"}

@router.post("/create_user/")
async def create_user(db: db_dependency, create_user_request: CreateUser):
    try:
        # Check if user already exists
        existing_user = db.query(Users).filter(
            (Users.email == create_user_request.email) |
            (Users.username == create_user_request.username) |
            (Users.phone_number == create_user_request.phone_number)
        ).first()
        
        if existing_user:
            if existing_user.email == create_user_request.email:
                raise HTTPException(status_code=400, detail="Email already registered")
            if existing_user.username == create_user_request.username:
                raise HTTPException(status_code=400, detail="Username already taken")
            if existing_user.phone_number == create_user_request.phone_number:
                raise HTTPException(status_code=400, detail="Phone number already registered")

        create_user_model = Users(
            email=create_user_request.email,
            username=create_user_request.username,
            first_name=create_user_request.first_name,
            last_name=create_user_request.last_name,
            phone_number=create_user_request.phone_number,
            hashed_password=bcrypt_context.hash(create_user_request.password[:72]),
            admin=create_user_request.admin
        )
        
        db.add(create_user_model)
        db.commit()
        db.refresh(create_user_model)
        return {"message": "User created successfully"}
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    
@router.get("/all_users/")
async def get_all_users(db: db_dependency):
    user_model = db.query(Users).all()
    return user_model
    
