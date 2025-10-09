from fastapi import APIRouter, Depends, HTTPException


router = APIRouter(
    prefix="/admin",
    tags=["admin"],)

@router.get("/test")
async def admin_test():
    return {"message": "Admin route is working!"}