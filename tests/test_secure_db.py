import logging
import pytest
from sqlalchemy.orm import Session

from tst_auth_svc.models.base import get_secure_db


def test_get_secure_db_success():
    # get_secure_db returns a generator; extract the session using next()
    gen = get_secure_db()
    session = next(gen)
    try:
        # Assert that the extracted session is an instance of Session
        assert isinstance(session, Session)
    finally:
        # Advance generator to trigger cleanup; ignore StopIteration
        try:
            next(gen)
        except StopIteration:
            pass
        if session and hasattr(session, 'close'):
            try:
                session.close()
            except Exception:
                pass


def test_get_secure_db_failure(monkeypatch, caplog):
    # Define a faulty session that always raises an exception
    def faulty_session(*args, **kwargs):
        raise Exception("Simulated connection error")

    # Monkeypatch sessionmaker to simulate failure
    monkeypatch.setattr('tst_auth_svc.models.base.sessionmaker', lambda bind: lambda: faulty_session())

    gen = get_secure_db()
    with pytest.raises(Exception) as excinfo:
        next(gen)

    assert "Simulated connection error" in str(excinfo.value)

    # Verify that error was logged
    error_logged = any("Simulated connection error" in record.message for record in caplog.records)
    assert error_logged
