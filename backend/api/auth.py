from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from core.deps import get_current_user
from core.security import create_access_token, verify_password
from database import get_db
from models.user import User
from schemas.user import Token, UserResponse

router = APIRouter(prefix="/auth", tags=["authentication"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


@router.post("/login", response_model=Token)
async def login(request: Request, db: Session = Depends(get_db)):
    """User login. Supports both form and JSON payloads."""
    content_type = (request.headers.get("content-type") or "").lower()
    username = ""
    password = ""

    if "application/json" in content_type:
        data = await request.json()
        username = (data.get("username") or "").strip()
        password = data.get("password") or ""
    else:
        form = await request.form()
        username = (form.get("username") or "").strip()
        password = form.get("password") or ""

    if not username or not password:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="username and password are required",
        )

    user = db.query(User).filter(User.username == username).first()

    if not user or not verify_password(password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="invalid username or password",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="account is disabled",
        )

    access_token = create_access_token(data={"sub": user.username, "role": user.role})

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": UserResponse.model_validate(user),
    }


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Get current user profile."""
    return current_user
