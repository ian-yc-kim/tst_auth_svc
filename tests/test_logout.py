import pytest
from fastapi import status

from tst_auth_svc.models.session import SessionToken


def test_successful_logout(client, db_session):
    # Create a session in the DB
    session_token = "test_token_123"
    new_session = SessionToken(user_id=1, session_token=session_token)
    db_session.add(new_session)
    db_session.commit()
    
    # Call the logout endpoint with the valid session token
    response = client.post("/logout", json={"session_token": session_token})
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "Logout successful" in data.get("message", "")

    # Verify that the session is deleted
    session_in_db = db_session.query(SessionToken).filter(SessionToken.session_token == session_token).first()
    assert session_in_db is None


def test_logout_invalid_token(client):
    # Use an invalid token
    response = client.post("/logout", json={"session_token": "non_existent_token"})
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    data = response.json()
    assert "Invalid or missing session token" in data.get("detail", "")
