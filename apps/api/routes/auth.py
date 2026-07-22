"""
Auth endpoints.
"""
from fastapi import APIRouter, Depends
from core.security.auth import get_current_user

router = APIRouter()

@router.post("/login")
async def login():
    return {"access_token": "token", "token_type": "bearer"}

@router.post("/register")
async def register():
    return {"status": "registered"}

@router.post("/refresh")
async def refresh():
    return {"access_token": "new_token", "token_type": "bearer"}

@router.get("/me")
async def get_me(user: dict = Depends(get_current_user)):
    return user
