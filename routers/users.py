from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Annotated
from schemas import CreateUser, Token, ChangePasswordRequest
from models import Users
from datetime import timedelta
from fastapi.security import OAuth2PasswordRequestForm
from . import auth
from .auth import get_current_user, bcrypt_context, get_db

router = APIRouter(
    prefix='/users',
    tags=['users']
)
db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]

###########################################################
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
async def get_all_users(user: user_dependency, db: db_dependency):
    if user.get('admin') is False:
        raise HTTPException(status_code=403, detail="You are not authorized to access this resource.")
    user_model = db.query(Users).all()
    return user_model

@router.get("/information/")
async def get_user_by_id(user: user_dependency, db: db_dependency):
    user_model = db.query(Users).filter(Users.id == user.get('id')).first()
    if not user_model:
        raise HTTPException(status_code=404, detail="User not found")
    return user_model

async def update_user_attribute(user_id: int, attribute: str, value: str, db: db_dependency):
    user_model = db.query(Users).filter(Users.id == user_id).first()
    if not user_model:
        raise HTTPException(status_code=404, detail="User not found")

    if attribute == "password":
        setattr(user_model, "hashed_password", bcrypt_context.hash(value[:72]))
    else:
        setattr(user_model, attribute, value)

    db.commit()
    db.refresh(user_model)
    return user_model

@router.put("/change_first_name/{user_model.id}")
async def change_first_name(user: user_dependency, new_first_name: str, db: db_dependency):
    user_model = db.query(Users).filter(Users.id == user.get('id')).first()
    return await update_user_attribute(user_model.id, "first_name", new_first_name, db)

@router.put("/change_last_name/{user_model.id}")
async def change_last_name(user: user_dependency, new_last_name: str, db: db_dependency):
    user_model = db.query(Users).filter(Users.id == user.get('id')).first()
    return await update_user_attribute(user_model.id, "last_name", new_last_name, db)
    
@router.put("/change_phone_number/{user_model.id}")
async def change_phone_number(user: user_dependency, new_phone_number: str, db: db_dependency):
    user_model = db.query(Users).filter(Users.id == user.get('id')).first()
    return await update_user_attribute(user_model.id, "phone_number", new_phone_number, db)

@router.put("/change_email/{user_model.id}")
async def change_email(user: user_dependency, new_email: str, db: db_dependency):
    user_model = db.query(Users).filter(Users.id == user.get('id')).first()
    return await update_user_attribute(user_model.id, "email", new_email, db)

@router.put("/change_password")
async def change_password(user: user_dependency, password_request: ChangePasswordRequest, db: db_dependency):
    user_model = db.query(Users).filter(Users.id == user.get('id')).first()
    if not bcrypt_context.verify(password_request.current_password, user_model.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect current password")
    if password_request.current_password == password_request.new_password:
            raise HTTPException(status_code=400, detail="New password must be different from the current password")
    user_model.hashed_password = bcrypt_context.hash(password_request.new_password[:72])
    db.commit()

    return {"message": "Password changed successfully"}

@router.put('/change_username/{user_model.id}')
async def change_username(user: user_dependency, new_username: str, db: db_dependency):
    user_model = db.query(Users).filter(Users.id == user.get('id')).first()
    return await update_user_attribute(user_model.id, "username", new_username, db)

@router.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: db_dependency
):
    user = auth.authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail='Could not validate user.')
    token = auth.create_access_token(user.username, user.id, user.admin, timedelta(minutes=20))

    return {'access_token': token, 'token_type': 'bearer'}