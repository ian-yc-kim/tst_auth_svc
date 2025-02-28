import bcrypt
from fastapi import status

from tst_auth_svc.models.user import User


def create_user_in_db(db, username: str, email: str, password: str):
    hashed_pw = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    user = User(username=username, email=email, password=hashed_pw)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def test_password_reset_valid(client, db_session):
    # Create a test user for password reset
    username = "resetuser"
    email = "resetuser@example.com"
    raw_password = "securepassword"
    create_user_in_db(db_session, username, email, raw_password)

    # Request password reset using email
    response = client.post("/password-reset", json={"identifier": email})
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "Password reset token generated successfully" in data.get("message", "")
    token = data.get("reset_token", "")
    assert token.startswith("reset:")


def test_password_reset_invalid(client):
    # Request password reset for a non-existent user
    response = client.post("/password-reset", json={"identifier": "nonexistent@example.com"})
    assert response.status_code == status.HTTP_404_NOT_FOUND
    data = response.json()
    assert "User not found" in data.get("detail", "")
