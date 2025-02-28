import logging

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr, validator
from sqlalchemy.orm import Session
import bcrypt

from tst_auth_svc.models.base import get_db
from tst_auth_svc.models.user import User

router = APIRouter()


class UserRegistrationRequest(BaseModel):
    username: str
    email: EmailStr
    password: str

    @validator('password')
    def password_min_length(cls, v):
        min_length = 6
        if len(v) < min_length:
            raise ValueError(f'Password must be at least {min_length} characters long')
        return v


class UserRegistrationResponse(BaseModel):
    message: str


@router.post('/register', response_model=UserRegistrationResponse)
def register_user(registration: UserRegistrationRequest, db: Session = Depends(get_db)):
    try:
        # Check for duplicate user by username or email
        existing_user = db.query(User).filter(
            (User.username == registration.username) | (User.email == registration.email)
        ).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User with this username or email already exists."
            )

        # Hash the password using bcrypt
        try:
            hashed_pw = bcrypt.hashpw(registration.password.encode('utf-8'), bcrypt.gensalt())
            # bcrypt.hashpw returns bytes, decode to string for storage
            hashed_pw_str = hashed_pw.decode('utf-8')
        except Exception as e:
            logging.error(e, exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error processing password encryption."
            )

        # Create new user instance
        new_user = User(
            username=registration.username,
            email=registration.email,
            password=hashed_pw_str
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        return UserRegistrationResponse(message="User registered successfully")
    except HTTPException:
        raise
    except Exception as e:
        logging.error(e, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed due to an internal error."
        )
