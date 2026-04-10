from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from sqlalchemy.orm import Session
from jose import jwt, JWTError

from app.schemas.user import UserCreate, UserLogin, RefreshRequest
from app.services.auth_service import register_user, login_user
from app.tasks.background_tasks import send_welcome_email
from app.db.session import get_db
from app.core.security import (
    create_access_token,
    get_current_user,
    token_blacklist,
    SECRET_KEY,
    ALGORITHM
)

# ✅ ONLY ONE router
router = APIRouter(prefix="/auth", tags=["Auth"])


# ✅ REGISTER
@router.post("/register")
def register(
    user: UserCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    new_user = register_user(db, user.email, user.password)
    send_welcome_email(background_tasks, user.email)
    return {"message": "User registered"}


# ✅ LOGIN
@router.post("/login")
def login(user: UserLogin, db: Session = Depends(get_db)):
    tokens = login_user(db, user.email, user.password)

    if not tokens:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    return tokens


# ✅ LOGOUT (FIXED)
@router.post("/logout")
def logout(user=Depends(get_current_user)):
    token = user.get("token")

    if token:
        token_blacklist.add(token)

    return {"message": "Logout successful"}


# ✅ REFRESH TOKEN
@router.post("/refresh")
def refresh_token(data: RefreshRequest):
    try:
        payload = jwt.decode(
            data.refresh_token, SECRET_KEY, algorithms=[ALGORITHM]
        )
        email = payload.get("sub")

        new_access_token = create_access_token({"sub": email})

        return {"access_token": new_access_token}

    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid refresh token")


# ✅ TEST AUTH
@router.get("/test-auth")
def test_auth(user=Depends(get_current_user)):
    return {"message": "You are authenticated", "user": user}
