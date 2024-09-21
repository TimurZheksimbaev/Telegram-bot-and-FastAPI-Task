from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from config import TOKEN_SECRET, TOKEN_ALGORITHM, TOKEN_EXPIRATION

# OAuth2 scheme for obtaining the token
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Pydantic model for token data
class TokenData(BaseModel):
    telegram_uid: Optional[str] = None

# Function to create JWT access token
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=TOKEN_EXPIRATION)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, TOKEN_SECRET, algorithm=TOKEN_ALGORITHM)
    return encoded_jwt

# Function to verify the JWT token
async def verify_token(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, TOKEN_SECRET, algorithms=[TOKEN_ALGORITHM])
        telegram_uid: str = payload.get("sub")
        if telegram_uid is None:
            raise credentials_exception
        return TokenData(telegram_uid=telegram_uid)
    except JWTError:
        raise credentials_exception

