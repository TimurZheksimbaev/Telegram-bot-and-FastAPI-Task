from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.templating import Jinja2Templates
from scheme import Token, UserCreate
from crud import create_user, get_user_by_telegram_uid, login, logout
from sqlalchemy.ext.asyncio import AsyncSession
from database.connect import get_db
from authentication.auth import TokenData, verify_token
# from logger import create_logger

templates = Jinja2Templates(directory="templates")

user_router = APIRouter(
    prefix="/api/users"
)

#user_router_logger = create_logger("logs/app.log", "user_router")

@user_router.get("/")
async def root(request: Request):
    #user_router_logger.info("User panel accessed")
    return templates.TemplateResponse(
        request=request,
        name="user.html"
    )

"""Login"""
@user_router.post("/login", response_model=Token)
async def login_with_telegram_uid(telegram_uid: str, db: AsyncSession = Depends(get_db)):
    #user_router_logger.info(f"User {telegram_uid} logged in")
    return await login(db, telegram_uid)


"""Logout"""
@user_router.post("/logout", response_model=dict)
async def logout_from_telegram(telegram_uid: str, db: AsyncSession = Depends(get_db)):
    #user_router_logger.info(f"User {telegram_uid} logged out")
    return await logout(db, telegram_uid)


"""Create user"""
@user_router.post("/create", response_model=UserCreate)
async def create_new_user(user: UserCreate, db: AsyncSession = Depends(get_db)):
    db_user = await create_user(db, user)
    #user_router_logger.info(f"User {user.telegram_uid} created")
    return db_user

"""Get user by telegram uid"""
@user_router.get("/info/{uid}", response_model=UserCreate)
async def read_user(uid: str, db: AsyncSession = Depends(get_db), token: TokenData = Depends(verify_token)):
    user = await get_user_by_telegram_uid(db, uid)
    #user_router_logger.info(f"User {uid} info accessed")
    return user