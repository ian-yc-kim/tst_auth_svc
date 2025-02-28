import bcrypt
from fastapi import status
import pytest

from tst_auth_svc.models.user import User
from tst_auth_svc.models.session import SessionToken

def create_user(db, username: str, email: str, password: str) -> User:
    hashed_pw = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    user = User(username=username, email=email, password=hashed_pw)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def create_reset_token(db, user_id: int, token: str) -> SessionToken:
    token_record = SessionToken(user_id=user_id, session_token=token)
    db.add(token_record)
    db.commit()
    db.refresh(token_record)
    return token_record


def test_valid_password_update(client, db_session):
    # Create a test user
    username = "testuser_update"
    email = "updateuser@example.com"
    original_password = "originalpass"
    user = create_user(db_session, username, email, original_password)

    # Create a valid reset token for this user
    reset_token = "reset:testvalidtoken12345"
    create_reset_token(db_session, user.id, reset_token)

    # New password to be updated
    new_password = "newsecurepassword"

    # Call the password update endpoint
    response = client.post("/password-update", json={"reset_token": reset_token, "new_password": new_password})
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "Password updated successfully" in data.get("message", "")

    # Verify that the user's password is updated and hashed correctly
    updated_user = db_session.query(User).filter(User.id == user.id).first()
    assert updated_user is not None
    assert updated_user.password != original_password
    assert bcrypt.checkpw(new_password.encode('utf-8'), updated_user.password.encode('utf-8'))

    # Verify that the reset token has been invalidated (deleted)
    token_record = db_session.query(SessionToken).filter(SessionToken.session_token == reset_token).first()
    assert token_record is None


def test_invalid_reset_token(client):
    # Use an invalid token to update password
    response = client.post("/password-update", json={"reset_token": "invalidtoken", "new_password": "anynewpass"})
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    data = response.json()
    assert "Invalid or expired reset token" in data.get("detail", "")


# Optional: Additional edge case tests can be added here
