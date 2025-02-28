import bcrypt
from fastapi import status

from tst_auth_svc.models.user import User


def create_user_in_db(db, username: str, password: str, email: str = "dummy@example.com"):
    hashed_pw = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    user = User(username=username, email=email, password=hashed_pw)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def test_successful_login(client, db_session):
    # Insert a test user into the database
    username = "testlogin"
    raw_password = "correctpassword"
    email = "testlogin@example.com"
    create_user_in_db(db_session, username, raw_password, email)
    
    response = client.post("/login", json={"username": username, "password": raw_password})
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "session_token" in data
    assert data["session_token"] != ""


def test_login_nonexistent_user(client):
    response = client.post("/login", json={"username": "nonexistent", "password": "any"})
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    data = response.json()
    assert "Invalid credentials" in data.get("detail", "")


def test_login_wrong_password(client, db_session):
    username = "userwrongpass"
    raw_password = "rightpassword"
    email = "userwrongpass@example.com"
    create_user_in_db(db_session, username, raw_password, email)
    
    # Attempt login with an incorrect password
    response = client.post("/login", json={"username": username, "password": "wrongpassword"})
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    data = response.json()
    assert "Invalid credentials" in data.get("detail", "")
