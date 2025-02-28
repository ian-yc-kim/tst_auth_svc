import logging
import pytest
from sqlalchemy.orm import Session

from tst_auth_svc.models.base import get_secure_db


# Test case to verify that get_secure_db returns a valid session

def test_get_secure_db_success():
    session = None
    try:
        session = get_secure_db()
        # Check that the returned session is an instance of Session
        assert isinstance(session, Session)
    finally:
        # Close the session if created to free resources
        if session and hasattr(session, 'close'):
            try:
                session.close()
            except Exception:
                pass


# Test case to simulate a connection failure and verify error logging and re-raising

def test_get_secure_db_failure(monkeypatch, caplog):
    # Define a faulty session that always raises an exception
    def faulty_session(*args, **kwargs):
        raise Exception("Simulated connection error")

    # Monkeypatch the sessionmaker in the module to simulate failure
    monkeypatch.setattr('tst_auth_svc.models.base.sessionmaker', lambda bind: lambda: faulty_session())

    with pytest.raises(Exception) as excinfo:
        get_secure_db()

    assert "Simulated connection error" in str(excinfo.value)

    # Check that the error was logged
    error_logged = any("Simulated connection error" in record.message for record in caplog.records)
    assert error_logged
