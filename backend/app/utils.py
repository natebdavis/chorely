from passlib.context import CryptContext
from jose import jwt
from datetime import datetime, timedelta
from dotenv import load_dotenv
import pathlib
import os
from pydantic import BaseModel
from fastapi.security import OAuth2PasswordBearer
from fastapi import HTTPException, status
from enum import Enum

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")
BUCKET = "images"

ALLOWED_IMAGE_TYPES = {
    "image/jpeg",
    "image/png",
    "image/webp",
    "image/gif"
}
ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png", "webp", "gif"}

MAX_FILE_SIZE = 50 * 1024 * 1024  # 50 MB

class DateFilter(str, Enum):
    TODAY = "today"
    WEEK = "week"
    MONTH = "month"


class Weekday(int, Enum):
    SUNDAY = 6
    MONDAY = 0
    TUESDAY = 1
    WEDNESDAY = 2
    THURSDAY = 3
    FRIDAY = 4
    SATURDAY = 5

def load_env_variables():
    """Loads environment variables from the .env file.
    Output: A dictionary containing the environment variables."""

    # Load environment variables from .env file in root folder
    load_dotenv(dotenv_path=pathlib.Path(__file__).resolve().parent.parent / '.env')

    env = {
        "SUPABASE_URL": os.getenv("SUPABASE_URL"),
        "SECRET_KEY": os.getenv("SECRET_KEY"),
        "SERVICE_KEY": os.getenv("SERVICE_KEY"),
        "ALGORITHM": os.getenv("ALGORITHM"),
        "ACCESS_TOKEN_EXPIRE_MINUTES": os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES")
    }
    return env

def verify_password(plain_password, hashed_password) -> bool:
    """Verifies that the provided plain password matches the hashed password.
    Inputs: `plain_password` is the password provided by the user, `hashed_password` is the password stored in the database.
    Output: `True` if the passwords match, `False` otherwise."""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password) -> str:
    """Hashes the provided password using bcrypt.
    Input: `password` is the plain password to be hashed.
    Output: The hashed password as a string."""
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    """Creates a JWT access token with the provided data and expiration time.
    Inputs: `data` is a dictionary containing the data to be included in the token, `expires_delta` is an optional timedelta for token expiration.
    Output: The generated JWT access token as a string."""
    env = load_env_variables()
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=int(env["ACCESS_TOKEN_EXPIRE_MINUTES"]))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, env["SECRET_KEY"], algorithm=env["ALGORITHM"])
    return encoded_jwt

class Token(BaseModel):
    """Model for JWT token response."""
    access_token: str
    token_type: str

class TokenData(BaseModel):
    """Model for data contained in JWT token."""
    username: str | None = None

credentials_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},)


