import uuid
import logging

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session
import bcrypt

from tst_auth_svc.models.base import get_db
from tst_auth_svc.models.user import User

router = APIRouter()


class LoginRequest(BaseModel):
    username: str
    password: str


class LoginResponse(BaseModel):
    session_token: str
    message: str = "Login successful"


@router.post("/login", response_model=LoginResponse)

def login_user(login_data: LoginRequest, db: Session = Depends(get_db)) -> LoginResponse:
    """Handles user login by verifying credentials and generating a session token.

    This endpoint accepts a username and plaintext password, verifies them against the
    stored credentials, and upon successful authentication, generates a session token.
    The token is stored in the sessions table for session management.

    Args:
        login_data (LoginRequest): Contains username and password in plaintext.
        db (Session): Database session provided via dependency injection.

    Returns:
        LoginResponse: Contains the generated session token and success message.

    Raises:
        HTTPException: With 401 status if credentials are invalid, or 500 for internal errors.
    """
    try:
        user = db.query(User).filter(User.username == login_data.username).first()
        if not user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
        
        if not bcrypt.checkpw(login_data.password.encode('utf-8'), user.password.encode('utf-8')):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
        
        # Generate session token using uuid4
        session_token = str(uuid.uuid4())

        # Import the SessionToken model and store the token in the sessions table
        from tst_auth_svc.models.session import SessionToken
        new_session = SessionToken(user_id=user.id, session_token=session_token)
        db.add(new_session)
        db.commit()
        
        return LoginResponse(session_token=session_token)
    except HTTPException:
        raise
    except Exception as e:
        logging.error(e, exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")
