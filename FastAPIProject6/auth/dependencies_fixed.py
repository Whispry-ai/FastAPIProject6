# auth/dependencies.py
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from jose.exceptions import ExpiredSignatureError
from sqlalchemy.orm import Session

from database import get_db
from models.user import User
from schemas import UserRole
from auth.jwt_handler import SECRET_KEY, ALGORITHM

# OAuth2 token scheme — points to the correct login endpoint
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/user_routes/login")
