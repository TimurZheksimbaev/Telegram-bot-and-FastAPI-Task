from datetime import timedelta, datetime
from typing import Dict
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import delete
from sqlalchemy.exc import NoResultFound
from database.models import User
from config import TOKEN_EXPIRATION
from fastapi import HTTPException, status
from authentication.auth import create_access_token

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
    await update_user(db, user.telegram_uid, {"last_login": datetime.now()})
    return {"access_token": access_token, "token_type": "bearer"}

async def logout(db: AsyncSession, telegram_uid: str) -> Dict[str, str]:
    user = await get_user_by_telegram_uid(db, telegram_uid)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Telegram UID",
        )
    # Update last_logout time in the database
    await update_user(db, user.telegram_uid, {"last_logout": datetime.now()})
    return {"message": "Logged out successfully"}

# Function to fetch a list of users with pagination
async def get_users(db: AsyncSession):
    try:
        result = await db.execute(select(User))
        return result.scalars().all()
    except NoResultFound:
        return HTTPException(status_code=404, detail="No users found")

async def get_user_by_telegram_uid(db: AsyncSession, telegram_uid: str) -> User | HTTPException:
    try:
        result = await db.execute(select(User).where(User.telegram_uid == telegram_uid))
        return result.scalar_one_or_none()
    except NoResultFound:
        return HTTPException(status_code=404, detail="No users found")

async def get_user_by_nickname(db: AsyncSession, nickname: str) -> User | HTTPException:
    try:
        result = await db.execute(select(User).where(User.nickname == nickname))
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

async def delete_user(db: AsyncSession, telegram_uid: str):
    try:
        result = await db.execute(select(User).where(User.telegram_uid == telegram_uid))
        user = result.scalar_one()
        if user:
            await db.execute(delete(User).where(User.telegram_uid == telegram_uid))
        await db.commit()
        return True
    except NoResultFound:
        return HTTPException(status_code=404, detail="No users found")

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
    except NoResultFound:
        return HTTPException(status_code=404, detail="User not found")



