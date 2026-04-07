from fastapi import Depends
from app.core.security import get_current_user
from app.core.security import create_access_token, SECRET_KEY, ALGORITHM
from fastapi import HTTPException
from jose import jwt, JWTError
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.schemas.user import UserCreate, UserLogin, RefreshRequest
from app.services.auth_service import register_user, login_user
from app.db.session import get_db
from app.core.security import create_access_token

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register")
def register(user: UserCreate, db: Session = Depends(get_db)):
    return register_user(db, user.email, user.password)


@router.post("/login")
def login(user: UserLogin, db: Session = Depends(get_db)):
    tokens = login_user(db, user.email, user.password)

    if not tokens:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    return tokens


@router.post("/refresh")
def refresh_token(data: RefreshRequest):
    try:
        payload = jwt.decode(data.refresh_token,
                             SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")

        new_access_token = create_access_token({"sub": email})

        return {"access_token": new_access_token}

    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid refresh token")


@router.get("/test-auth")
def test_auth(user=Depends(get_current_user)):
    return {"message": "You are authenticated", "user": user}
