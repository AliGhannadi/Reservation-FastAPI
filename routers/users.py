from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from db import SessionLocal
from typing import Annotated, Literal
from schemas import CreateUser, Token
from models import Users
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from jose import jwt, JWTError
from datetime import datetime, timedelta, timezone
# Password hashing configuration
SECRET_KEY = '197b2c37c391bed93fe80344fe73b806947a65e36206e05a1a23c2fa12702fe3'
ALGORITHM = 'HS256'
bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_bearer = OAuth2PasswordBearer(tokenUrl='users/token')
router = APIRouter(
    prefix='/users',
    tags=['users']
)
#######################################################
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def authenticate_user(username: str, password: str, db):
    user = db.query(Users).filter(Users.username == username).first()
    if not user:
        return False
    if not bcrypt_context.verify(password, user.hashed_password):
        return False
    return user


def create_access_token(username: str, user_id: int, expires_delta: timedelta):
    encode = {'sub': username, 'id': user_id}
    expires = datetime.now() + expires_delta
    encode.update({'exp': expires})
    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)


async def get_current_user(token: Annotated[str, Depends(oauth2_bearer)]):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get('sub')
        user_id: int = payload.get('id')
        if username is None or user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail='Could not validate user.')
        return {'username': username, 'id': user_id}
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail='Could not validate user.')
#################################################

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
async def get_all_users(db: db_dependency):
    user_model = db.query(Users).all()
    return user_model

@router.get("/{user_id}")
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

@router.put("/change_first_name/{user_id}")
async def change_first_name(user_id: int, new_first_name: str, db: db_dependency):
    return await update_user_attribute(user_id, "first_name", new_first_name, db)

@router.put("/change_last_name/{user_id}")
async def change_last_name(user_id: int, new_last_name: str, db: db_dependency):
    return await update_user_attribute(user_id, "last_name", new_last_name, db)
    
@router.put("/change_phone_number/{user_id}")
async def change_phone_number(user_id: int, new_phone_number: str, db: db_dependency):
    return await update_user_attribute(user_id, "phone_number", new_phone_number, db)

@router.put("/change_email/{user_id}")
async def change_email(user_id: int, new_email: str, db: db_dependency):
    return await update_user_attribute(user_id, "email", new_email, db)

@router.put("/change_password/{user_id}")
async def change_password(user_id: int, new_password: str, db: db_dependency):
    return await update_user_attribute(user_id, "password", new_password, db)

@router.put('/change_username/{user_id}')
async def change_username(user_id: int, new_username: str, db: db_dependency):
    return await update_user_attribute(user_id, "username", new_username, db)

@router.post("/token", response_model=Token)
async def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
                                 db: db_dependency):
    user = authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail='Could not validate user.')
    token = create_access_token(user.username, user.id, timedelta(minutes=20))

    return {'access_token': token, 'token_type': 'bearer'}