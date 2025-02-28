from sqlalchemy import Column, PrimaryKeyConstraint, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker, Session
import logging

from tst_auth_svc.config import DATABASE_URL

Base = declarative_base()

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)


def get_db() -> Session:
    session = scoped_session(sessionmaker(bind=engine))
    try:
        yield session
    finally:
        session.close()


def get_secure_db() -> Session:
    """Creates a secure database session with enhanced error management.

    This function attempts to create a new session using SQLAlchemy's sessionmaker
    bound to the global engine. In case of any exception during session creation, the
    error is logged with detailed traceback and then re-raised to signal failure.
    """
    try:
        # Attempt to create a new session using sessionmaker bound to the engine
        session = sessionmaker(bind=engine)()
        # Return the session if creation is successful
        return session
    except Exception as e:
        # Log the exception with error details and traceback
        logging.error(e, exc_info=True)
        # Reraise the exception to indicate failure of secure session creation
        raise
