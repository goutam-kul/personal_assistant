from datetime import timedelta
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException, status
from app.utils.password_utils import get_password_hash
from app.utils.auth import create_access_token
from app.config.settings import settings
from app.schemas import user
from app.db.database import get_db
from app import crud

router = APIRouter()

# 1. Register a new user
@router.post("/users/", response_model=user.UserResponse)
async def create_user(user: user.UserCreate, db: Session = Depends(get_db)):
    try:
            
        # Validate password length
        if len(user.password) < 8:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Password must be at least 8 characters long."
            )
        
        # Check if the email or username is already registered
        if crud.get_user_by_email(db=db, email=user.email) or crud.get_user_by_id(db=db, user_id=user.user_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username or Email is already registered."
            )
        
        # Hash password
        hashed_password = get_password_hash(password=user.password)

        # Create the user
        return crud.create_user(db=db, user=user, hashed_password=hashed_password)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating user: {str(e)}"
        )
    
    
# 2. Login User
@router.post("/auth/login")
async def login(request: user.LoginRequest, db: Session = Depends(get_db)):
    if not request.user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User ID is required"
        )
    auth_user = crud.authenticate_user(
        db=db,
        password=request.password,
        user_id=request.user_id
    )
    
    if not auth_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Credentials"
        )
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": auth_user.user_id}, expires_delta=access_token_expires
    )

    return user.LoginResponse(
        access_token=access_token,
        token_type="bearer"
    )


@router.get("/users/list")
async def list_users(db: Session = Depends(get_db)):
    try:
        users = crud.list_user(db=db)
        if not users:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No users found"
            )
        return users
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error connecting to server {str(e)}"
        )