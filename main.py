from fastapi import FastAPI
import models
from db import engine
from routers import admin, users, reserve, doctor

app = FastAPI()

models.Base.metadata.create_all(bind=engine)

app.include_router(admin.router)
app.include_router(reserve.router)
app.include_router(users.router)
app.include_router(doctor.router)

@app.get("/")
async def read_root():
    return "Hello World"


            