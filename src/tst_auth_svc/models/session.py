from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from datetime import datetime

from tst_auth_svc.models.base import Base


class SessionToken(Base):
    """Model for storing user session tokens."""
    __tablename__ = 'sessions'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    session_token = Column(String(255), nullable=False, unique=True)
    created_at = Column(DateTime, default=datetime.utcnow)
