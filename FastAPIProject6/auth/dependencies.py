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


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    """
    Extracts and validates the current user from the JWT access token.
    """
    credentials_error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid credentials or token",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        # Decode token
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_uid: str = payload.get("sub")
        token_version: int = payload.get("ver", 0)

        if not user_uid:
            raise credentials_error

    except ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Access token has expired")
    except JWTError:
        raise credentials_error

    # Validate user from DB
    user = db.query(User).filter(User.user_uid == user_uid).first()
    if not user or user.token_version != token_version:
        raise HTTPException(status_code=401, detail="Invalid or revoked token")

    return user


# -----------------------------------------------------------------------------
# 🧩 Role-based Dependencies
# -----------------------------------------------------------------------------
def require_role(role: UserRole):
    """
    Dependency factory: restricts route access to users with the required role or higher.
    Example: @router.get("/admin", dependencies=[Depends(require_role(UserRole.ADMIN))])
    """
    def role_checker(current_user: User = Depends(get_current_user)):
        if current_user.role < role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Permission denied: insufficient role"
            )
        return current_user
    return role_checker


def admin_required(current_user: User = Depends(get_current_user)) -> User:
    """
    Restrict access to admins only.
    """
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admins only"
        )
    return current_user


def admin_or_employee_required(current_user: User = Depends(get_current_user)) -> User:
    """
    Allow access for admin or employee roles.
    """
    if current_user.role not in (UserRole.ADMIN, UserRole.EMPLOYEE):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission for this action"
        )
    return current_user
