import logging

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from tst_auth_svc.models.session import SessionToken
from tst_auth_svc.models.base import get_db

router = APIRouter()


class LogoutRequest(BaseModel):
    session_token: str


class LogoutResponse(BaseModel):
    message: str


@router.post("/logout", response_model=LogoutResponse)
def logout(request: LogoutRequest, db: Session = Depends(get_db)) -> LogoutResponse:
    try:
        session_record = db.query(SessionToken).filter(SessionToken.session_token == request.session_token).first()
        if not session_record:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or missing session token")
        db.delete(session_record)
        db.commit()
        return LogoutResponse(message="Logout successful")
    except HTTPException as he:
        raise he
    except Exception as e:
        logging.error(e, exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")
