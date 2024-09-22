from typing import Dict

from fastapi import APIRouter, HTTPException, Depends, Request, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from scheme import UserCreate, UserUpdate
from database.connect import get_db
from crud import get_users, update_user, delete_user, get_user_by_telegram_uid, get_user_by_nickname
from authentication.auth import verify_token
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from datetime import datetime

templates = Jinja2Templates(directory="templates")

admin_router = APIRouter(
    prefix="/api/admin"
)



@admin_router.get("/")
def root(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="admin.html"
    )


"""Stats"""
@admin_router.get("/stats")
async def get_user_stats(db: AsyncSession = Depends(get_db), admin: str = Depends(verify_token)):
    users = await get_users(db)
    total_users = len(users)
    online_users = sum(1 for user in users if (datetime.now() - user.last_login).seconds < 300)
    high_rating_users = [user for user in users if user.rating >= 5 and user.coins >= 60]
    
    return {
        "total_users": total_users,
        "online_users": online_users,
        "high_rating_users_count": len(high_rating_users)
    }

"""Get user by telegram uid"""
@admin_router.get("/get_user_by_uid/{uid}", response_model=UserCreate)
async def read_user(uid: str, db: AsyncSession = Depends(get_db), admin: str = Depends(verify_token)):
    user = await get_user_by_telegram_uid(db, uid)
    return user

@admin_router.get("/get_user_by_nickname/{nickname}", response_model=UserCreate)
async def read_user_by_nickname(nickname: str, db: AsyncSession = Depends(get_db), admin: str = Depends(verify_token)):
    user = await get_user_by_nickname(db, nickname)
    return user

"""Delete user"""
@admin_router.delete("/delete_user/{uid}")
async def delete_user_data(uid: str, db: AsyncSession = Depends(get_db), admin: str = Depends(verify_token)):
    deleted_user = await delete_user(db, uid)
    return deleted_user


"""Get all users"""
@admin_router.get("/get_users")
async def read_users(db: AsyncSession = Depends(get_db), admin = Depends(verify_token)):
    users = await get_users(db)
    return users


"""Update user"""
@admin_router.put("/update_user/{uid}", response_model=UserUpdate)
async def update_existing_user(uid: str, user: UserUpdate, db: AsyncSession = Depends(get_db), admin = Depends(verify_token)):
    updated_data = user.dict(exclude_unset=True)
    updated_user = await update_user(db, uid, updated_data)
    return updated_user


