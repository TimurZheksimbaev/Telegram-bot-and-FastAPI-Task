from datetime import timedelta
from typing import Dict

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import NoResultFound
from database.models import User
from config import TOKEN_EXPIRATION
from fastapi import HTTPException, status
from auth import create_access_token

async def login(db: AsyncSession, telegram_uid: str):
    user = await get_user_by_telegram_uid(db, telegram_uid)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Telegram UID",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=TOKEN_EXPIRATION)
    access_token = create_access_token(
        data={"sub": user.telegram_uid}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

# Function to fetch a list of users with pagination
async def get_users(db: AsyncSession, skip: int = 0, limit: int = 10):
    try:
        result = await db.execute(select(User).offset(skip).limit(limit))
        return result.scalars().all()
    except NoResultFound:
        return HTTPException(status_code=404, detail="No users found")

# Function to fetch a user by Telegram UID
async def get_user_by_uid(db: AsyncSession, uid: str):
    try:
        result = await db.execute(select(User).where(User.telegram_uid == uid))
        return result.scalar_one()
    except NoResultFound:
        return HTTPException(status_code=404, detail="No users found")

async def get_user_by_telegram_uid(db: AsyncSession, telegram_uid: str):
    try:
        result = await db.execute(select(User).where(User.telegram_uid == telegram_uid))
        return result.scalar_one_or_none()
    except NoResultFound:
        return HTTPException(status_code=404, detail="No users found")
# Function to create a new user
async def create_user(db: AsyncSession, user):
    db_user = User(
        nickname=user.nickname,
        telegram_uid=user.telegram_uid,
        coins=user.coins,
        rating=user.rating,
        last_login=user.last_login,
        last_logout=user.last_logout,
    )
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user

# Function to update user data
async def update_user(db: AsyncSession, uid: str, new_data: Dict[str, str]):
    try:
        result = await db.execute(select(User).where(User.telegram_uid == uid))
        user = result.scalar_one()

        for key, value in new_data.items():
            if hasattr(user, key):
                setattr(user, key, value)

        await db.commit()
        await db.refresh(user)
        return user
    except NoResultFound:
        return HTTPException(status_code=404, detail="No users found")

async def update_user_rating(db: AsyncSession, uid: str, newRating: int):
    try:
        result = await db.execute(select(User).where(User.telegram_uid == uid))
        user = result.scalar_one()
        user.rating = newRating
        await db.commit()
        await db.refresh(user)
        return user
    except NoResultFound:
        return HTTPException(status_code=404, detail="User not found")

async def add_coins(db: AsyncSession, uid: str, coinsAmount: int):
    try:
        result = await db.execute(select(User).where(User.telegram_uid == uid))
        user = result.scalar_one()
        user.coins += coinsAmount
        await db.commit()
        await db.refresh(user)
        return user
    except:
        return HTTPException(status_code=404, detail="User not found")



