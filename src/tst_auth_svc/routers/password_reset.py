import secrets
import logging

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from tst_auth_svc.models.user import User
from tst_auth_svc.models.session import SessionToken
from tst_auth_svc.models.base import get_db


router = APIRouter()


class PasswordResetRequest(BaseModel):
    identifier: str


class PasswordResetResponse(BaseModel):
    message: str
    reset_token: str = None  # Included for testing purposes, remove in production if needed


@router.post("/password-reset", response_model=PasswordResetResponse)
def password_reset(request: PasswordResetRequest, db: Session = Depends(get_db)) -> PasswordResetResponse:
    try:
        # Query the user by username or email
        user = db.query(User).filter((User.username == request.identifier) | (User.email == request.identifier)).first()
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

        # Generate a secure reset token with a prefix to indicate its type
        token = "reset:" + secrets.token_urlsafe(32)

        try:
            # Store the token using the existing SessionToken model
            new_session = SessionToken(user_id=user.id, session_token=token)
            db.add(new_session)
            db.commit()
        except Exception as e:
            logging.error(e, exc_info=True)
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error storing reset token")

        return PasswordResetResponse(message="Password reset token generated successfully", reset_token=token)
    except HTTPException:
        raise
    except Exception as e:
        logging.error(e, exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")
