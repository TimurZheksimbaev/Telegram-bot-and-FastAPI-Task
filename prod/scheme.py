from typing import Optional

from pydantic import BaseModel, Field
import datetime

# Pydantic model for creating and updating a user
class UserCreate(BaseModel):
    nickname: str
    telegram_uid: str
    coins: int = 0
    rating: int = 0
    last_login: datetime.datetime = datetime.datetime.now(datetime.UTC)
    last_logout: datetime.datetime = datetime.datetime.now(datetime.UTC)


class Token(BaseModel):
    access_token: str
    token_type: str

class UserUpdate(BaseModel):
    nickname: Optional[str] = Field(None, example="new_nickname")
    telegram_uid: Optional[str] = Field(None, example="123456789")
    coins: Optional[int] = Field(None, example=50)
    rating: Optional[int] = Field(None, example=4)
    last_login: Optional[datetime.datetime] = None
    last_logout: Optional[datetime.datetime] = None