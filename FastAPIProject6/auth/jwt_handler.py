# auth/jwt_handler.py
import os
from jose import jwt
from datetime import datetime, timedelta
from passlib.context import CryptContext

# Secret key and algorithm
SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    raise RuntimeError("SECRET_KEY environment variable is required for JWT signing")

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60000   # ~41 days
REFRESH_TOKEN_EXPIRE_DAYS = 7

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# Access Token (includes token_version)
def create_access_token(data: dict, token_version: int):
    to_encode = data.copy()
    if "sub" not in to_encode:
        raise ValueError("Access token payload must include 'sub' claim")

    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire, "ver": token_version})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


# Refresh Token (differentiate with type)
def create_refresh_token(data: dict):
    to_encode = data.copy()
    if "sub" not in to_encode:
        raise ValueError("Refresh token payload must include 'sub' claim")

    expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


# Password utils
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)
