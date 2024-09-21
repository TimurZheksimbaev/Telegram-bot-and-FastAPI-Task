from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import declarative_base
import datetime

# Используем AsyncAttrs для асинхронной работы с SQLAlchemy
Base = declarative_base(cls=AsyncAttrs)

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    nickname = Column(String, unique=True, index=True, nullable=False)
    telegram_uid = Column(String, unique=True, index=True, nullable=False)
    coins = Column(Integer, default=0)
    rating = Column(Integer, default=0)
    last_login = Column(DateTime, default=datetime.datetime.now())
    last_logout = Column(DateTime, default=datetime.datetime.now()+datetime.timedelta(minutes=10))
