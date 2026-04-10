from app.db.session import SessionLocal
from app.core.security import hash_password
from app.models.user import User

# 🔥 IMPORTANT: load all models
from app.db.base import Base


def create_admin():
    db = SessionLocal()

    existing = db.query(User).filter(User.email == "admin@gmail.com").first()

    if existing:
        print("⚠️ Admin already exists")
        return

    admin = User(
        email="admin@gmail.com",
        password=hash_password("admin123"),
        role="ADMIN"
    )

    db.add(admin)
    db.commit()
    db.close()

    print("✅ Admin created successfully")


if __name__ == "__main__":
    create_admin()
