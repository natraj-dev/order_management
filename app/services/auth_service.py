from app.core.security import create_access_token, create_refresh_token
from sqlalchemy.orm import Session
from app.models.user import User
from app.core.security import hash_password, verify_password, create_access_token


def register_user(db: Session, email: str, password: str):
    user = User(
        email=email,
        password=hash_password(password)
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def login_user(db, email, password):
    user = db.query(User).filter(User.email == email).first()

    if not user or not verify_password(password, user.password):
        return None

    access_token = create_access_token({
        "sub": user.email,
        "role": user.role
    })

    refresh_token = create_refresh_token({
        "sub": user.email
    })

    return {
        "access_token": access_token,
        "refresh_token": refresh_token
    }
