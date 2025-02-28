import logging
import bcrypt
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from tst_auth_svc.models.base import get_db
from tst_auth_svc.models.session import SessionToken
from tst_auth_svc.models.user import User


router = APIRouter()


class PasswordUpdateRequest(BaseModel):
    reset_token: str
    new_password: str = Field(..., min_length=6, description="New password, at least 6 characters long")


class PasswordUpdateResponse(BaseModel):
    message: str


@router.post("/password-update", response_model=PasswordUpdateResponse)
def update_password(request: PasswordUpdateRequest, db: Session = Depends(get_db)) -> PasswordUpdateResponse:
    try:
        # Find the reset token in the database
        token_record = db.query(SessionToken).filter(SessionToken.session_token == request.reset_token).first()
        if not token_record:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or expired reset token")

        # Find the associated user
        user = db.query(User).filter(User.id == token_record.user_id).first()
        if not user:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User not found for the provided token")

        try:
            # Hash the new password using bcrypt
            hashed_pw = bcrypt.hashpw(request.new_password.encode('utf-8'), bcrypt.gensalt())
            hashed_pw_str = hashed_pw.decode('utf-8')
        except Exception as e:
            logging.error(e, exc_info=True)
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error hashing the new password")

        # Update user's password
        user.password = hashed_pw_str

        # Invalidate the used reset token
        db.delete(token_record)
        db.commit()

        return PasswordUpdateResponse(message="Password updated successfully")
    except HTTPException as he:
        raise he
    except Exception as e:
        logging.error(e, exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")
