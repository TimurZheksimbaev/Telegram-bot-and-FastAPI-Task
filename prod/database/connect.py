from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import declarative_base
from datetime import datetime

# Используем AsyncAttrs для асинхронной работы с SQLAlchemy
Base = declarative_base(cls=AsyncAttrs)

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    nickname = Column(String, unique=True, index=True, nullable=False)
    telegram_uid = Column(String, unique=True, index=True, nullable=False)
    coins = Column(Integer, default=0)
    rating = Column(Integer, default=0)
    last_login = Column(DateTime, default=datetime.utcnow)
    last_logout = Column(DateTime, default=datetime.utcnow)


DATABASE_URL = "postgresql+asyncpg://postgres:postgres@localhost:5432/fastapitask"

# Создание асинхронного движка для подключения к базе данных
engine = create_async_engine(DATABASE_URL, echo=True)

# Асинхронная сессия для взаимодействия с базой данных
async_session = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)

async def init_db():
    async with engine.begin() as conn:
        # Create all tables
        await conn.run_sync(Base.metadata.create_all)

async def get_db() -> AsyncSession:
    async with async_session() as session:
        yield session