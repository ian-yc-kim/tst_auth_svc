from sqlalchemy import Column, PrimaryKeyConstraint, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker, Session
from typing import Generator
import logging

from tst_auth_svc.config import DATABASE_URL

Base = declarative_base()

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)


def get_db() -> Generator[Session, None, None]:
    session = scoped_session(sessionmaker(bind=engine))
    try:
        yield session
    finally:
        session.close()


def get_secure_db() -> Generator[Session, None, None]:
    """Creates a secure database session with enhanced error management.

    This function attempts to create a new session using SQLAlchemy's sessionmaker bound
    to the global engine. In case of any exception during session creation, the error
    is logged with detailed traceback and then re-raised to signal failure.

    It uses a scoped session factory for thread safety. This generator function yields a
    proper SQLAlchemy Session instance, ensuring that FastAPI's dependency injection can
    manage the connection lifecycle. Any errors encountered during session creation are
    logged and propagated, ensuring robust error handling.
    """
    session_instance = None
    try:
        # Create a scoped session factory and obtain a Session instance
        session_factory = scoped_session(sessionmaker(bind=engine))
        session_instance = session_factory()
        yield session_instance
    except Exception as e:
        logging.error(e, exc_info=True)
        raise
    finally:
        if session_instance:
            session_instance.close()
