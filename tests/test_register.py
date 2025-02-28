import json
import bcrypt
import pytest
from fastapi import status


# Using the 'client' and 'db_session' fixtures from tests/conftest.py

def test_valid_registration(client, db_session):
    payload = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "strongpassword"
    }
    response = client.post("/register", json=payload)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data.get("message") == "User registered successfully"

    # Verify that the password stored is hashed and not equal to the raw password
    from tst_auth_svc.models.user import User
    user = db_session.query(User).filter(User.username == "testuser").first()
    assert user is not None
    assert user.password != payload["password"]
    # Verify that the stored password is a valid bcrypt hash
    assert bcrypt.checkpw(payload["password"].encode('utf-8'), user.password.encode('utf-8'))


def test_duplicate_registration(client):
    payload = {
        "username": "duplicateuser",
        "email": "dup@example.com",
        "password": "anotherstrongpassword"
    }
    # First registration should succeed
    response1 = client.post("/register", json=payload)
    assert response1.status_code == status.HTTP_200_OK

    # Second registration with same username/email should fail
    response2 = client.post("/register", json=payload)
    assert response2.status_code == status.HTTP_400_BAD_REQUEST
    data = response2.json()
    assert "already exists" in data.get("detail", "")


def test_invalid_email_registration(client):
    payload = {
        "username": "invalidemailuser",
        "email": "notanemail",
        "password": "validpassword"
    }
    response = client.post("/register", json=payload)
    # Pydantic should catch the invalid email and return a 422 Unprocessable Entity error
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_short_password_registration(client):
    payload = {
        "username": "shortpwuser",
        "email": "shortpw@example.com",
        "password": "123"
    }
    response = client.post("/register", json=payload)
    # Expect a validation error for short password
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
