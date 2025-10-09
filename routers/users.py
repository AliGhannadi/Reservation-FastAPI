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

@router.get("/{user_id}")
async def get_user_by_id(user_id: int, db: db_dependency):
    user_model = db.query(Users).filter(Users.id == user_id).first()
    if not user_model:
        raise HTTPException(status_code=404, detail="User not found")
    return user_model

@router.put("/change_first_name/{user_id}")
async def change_first_name(user_id: int, new_first_name: str, db: db_dependency):
    user_model = db.query(Users).filter(Users.id == user_id).first()
    if not user_model:
        raise HTTPException(status_code=404, detail="User not found")
    user_model.first_name = new_first_name
    db.commit()
    db.refresh(user_model)
    return user_model

@router.put("/change_last_name/{user_id}")
async def change_last_name(user_id: int, new_last_name: str, db: db_dependency):
    user_model = db.query(Users).filter(Users.id == user_id).first()
    if not user_model:
     raise HTTPException(status_code=404, detail="User not found")
    user_model.last_name = new_last_name
    
@router.put("/change_phone_number/{user_id}")
async def change_phone_number(user_id: int, new_phone_number: str, db: db_dependency):
    user_model = db.query(Users).filter(Users.id == user_id).first()
    if not user_model:
        raise HTTPException(status_code=404, detail="User not found")
    user_model.phone_number = new_phone_number
    db.commit()
    db.refresh(user_model)
    return user_model

@router.put("/change_email/{user_id}")
async def change_email(user_id: int, new_email: str, db: db_dependency):
    user_model = db.query(Users).filter(Users.id == user_id).first()
    if not user_model:
        raise HTTPException(status_code=404, detail="User not found")
    user_model.email = new_email
    db.commit()
    db.refresh(user_model)
    return user_model
@router.put("/change_password/{user_id}")
async def change_password(user_id: int, new_password: str, db: db_dependency):
    user_model = db.query(Users).filter(Users.id == user_id).first()
    if not user_model:
        raise HTTPException(status_code=404, detail="User not found")
    user_model.hashed_password = bcrypt_context.hash(new_password[:72])
    db.commit()
    db.refresh(user_model)
    return user_model

@router.put('/change_username/{user_id}')
async def change_username(user_id: int, new_username: str, db: db_dependency):
    user_model = db.query(Users).filter(Users.id == user_id).first()
    if not user_model:
        raise HTTPException(status_code=404, detail="User not found")
    user_model.username = new_username
    db.commit()
    db.refresh(user_model)
    return user_model


    
