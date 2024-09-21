from fastapi import FastAPI, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from database.connect import init_db, get_db
from auth import TokenData, verify_token
from scheme import UserCreate, Token, UserUpdate
from crud import get_users, get_user_by_uid, create_user, update_user, login
from fastapi.templating import Jinja2Templates

app = FastAPI(on_startup=[init_db])

templates = Jinja2Templates(directory="templates")

@app.get("/")
async def root(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html"
    )

@app.post("/token", response_model=Token)
async def login_with_telegram_uid(telegram_uid: str, db: AsyncSession = Depends(get_db)):
    return await login(db, telegram_uid)

# Endpoint to get a list of users
@app.get("/users", response_model=list[UserCreate], )
async def read_users(skip: int = 0, limit: int = 10, db: AsyncSession = Depends(get_db), token: TokenData = Depends(verify_token)):
    users = await get_users(db, skip=skip, limit=limit)
    return users

# Endpoint to get a user by Telegram UID
@app.get("/users/{uid}", response_model=UserCreate)
async def read_user(uid: str, db: AsyncSession = Depends(get_db), token: TokenData = Depends(verify_token)):
    user = await get_user_by_uid(db, uid)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user

# Endpoint to create a new user
@app.post("/users", response_model=UserCreate)
async def create_new_user(user: UserCreate, db: AsyncSession = Depends(get_db), token: TokenData = Depends(verify_token)):
    db_user = await create_user(db, user)
    return db_user

# Endpoint to update user data
@app.put("/users/{uid}", response_model=UserUpdate)
async def update_existing_user(uid: str, user: UserUpdate, db: AsyncSession = Depends(get_db), token: TokenData = Depends(verify_token)):
    updated_data = user.dict(exclude_unset=True)

    updated_user = await update_user(db, uid, updated_data)
    if updated_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return updated_user

