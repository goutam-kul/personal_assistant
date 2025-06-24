from typing import Optional
from sqlalchemy.orm import Session
from app.schemas import user
from app import models
from app.utils.password_utils import get_password_hash, verify_password

# ---------- USER ----------

def create_user(db: Session, user: user.UserCreate, hashed_password: str):
    db_user = models.User(
        user_id=user.user_id,
        email=user.email,
        password_hash=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def get_user_by_id(db: Session, user_id: str):
    return db.query(models.User).filter(models.User.user_id == user_id).first()

def delete_user(db: Session, user_id: str):
    user = get_user_by_id(db, user_id)
    if user:
        db.delete(user)
        db.commit()
    return user

def authenticate_user(
    db: Session,
    password: str,
    user_id: str
):
    if user_id:
        user = db.query(models.User).filter(models.User.user_id==user_id).first()
    else:
        user = None

    if not user or not verify_password(password, user.password_hash):
        return None
    
    return user

# for testing 
def list_user(db: Session):
    users = db.query(models.User).all()
    return users


# ---------- TASKS ---------
