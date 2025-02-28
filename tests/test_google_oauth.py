import os
import uuid
import pytest
import logging

from fastapi import status


def test_google_login_redirect(monkeypatch, client):
    # Set environment variables
    monkeypatch.setenv('GOOGLE_CLIENT_ID', 'test_client_id')
    monkeypatch.setenv('GOOGLE_CLIENT_SECRET', 'test_client_secret')
    monkeypatch.setenv('GOOGLE_REDIRECT_URI', 'http://testserver/google-callback')

    # Mock the generate_auth_url function in the google_oauth router since it was imported at module level
    def fake_generate_auth_url(client_id, redirect_uri):
        return 'http://fake.google.auth/url'

    monkeypatch.setattr('tst_auth_svc.routers.google_oauth.generate_auth_url', fake_generate_auth_url)

    # Prevent automatic redirection so we can inspect the redirect response
    response = client.get('/google-login', follow_redirects=False)
    # RedirectResponse typically returns status code 307 or 302
    assert response.status_code in [307, 302]
    # Ensure redirection URL is as expected
    assert response.headers.get('location') == 'http://fake.google.auth/url'


def test_google_callback_success(monkeypatch, client, db_session):
    # Set environment variables
    monkeypatch.setenv('GOOGLE_CLIENT_ID', 'test_client_id')
    monkeypatch.setenv('GOOGLE_CLIENT_SECRET', 'test_client_secret')
    monkeypatch.setenv('GOOGLE_REDIRECT_URI', 'http://testserver/google-callback')

    # Prepare a fake token response
    fake_tokens = {
        'access_token': 'dummy_access_token',
        'id_token': 'dummy_id_token',
        'email': 'testuser@example.com'
    }

    # Monkeypatch the exchange_code_for_tokens function in the google_oauth module
    def fake_exchange_code_for_tokens(code, client_id, client_secret, redirect_uri):
        if code == 'valid_code':
            return fake_tokens
        raise Exception('Invalid code')

    monkeypatch.setattr('tst_auth_svc.routers.google_oauth.exchange_code_for_tokens', fake_exchange_code_for_tokens)

    # Insert a test user in the db
    from tst_auth_svc.models.user import User
    test_user = User(username='testuser', email='testuser@example.com', password='dummy')
    db_session.add(test_user)
    db_session.commit()
    db_session.refresh(test_user)

    response = client.get('/google-callback', params={'code': 'valid_code'})
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert 'session_token' in data
    # Verify session_token is a valid uuid
    uuid_obj = uuid.UUID(data['session_token'])


def test_google_callback_missing_code(client):
    response = client.get('/google-callback')
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    data = response.json()
    assert 'Authorization code is missing' in data.get('detail', '')


def test_google_callback_invalid_tokens(monkeypatch, client):
    # Set environment variables
    monkeypatch.setenv('GOOGLE_CLIENT_ID', 'test_client_id')
    monkeypatch.setenv('GOOGLE_CLIENT_SECRET', 'test_client_secret')
    monkeypatch.setenv('GOOGLE_REDIRECT_URI', 'http://testserver/google-callback')

    # Monkeypatch the exchange function to return incomplete tokens
    def fake_exchange_code_for_tokens(code, client_id, client_secret, redirect_uri):
        return {'access_token': 'dummy'}  # missing id_token and email

    monkeypatch.setattr('tst_auth_svc.routers.google_oauth.exchange_code_for_tokens', fake_exchange_code_for_tokens)

    response = client.get('/google-callback', params={'code': 'any_code'})
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    data = response.json()
    assert 'Invalid token exchange response' in data.get('detail', '')


def test_google_callback_user_not_found(monkeypatch, client, db_session):
    # Set environment variables
    monkeypatch.setenv('GOOGLE_CLIENT_ID', 'test_client_id')
    monkeypatch.setenv('GOOGLE_CLIENT_SECRET', 'test_client_secret')
    monkeypatch.setenv('GOOGLE_REDIRECT_URI', 'http://testserver/google-callback')

    fake_tokens = {
        'access_token': 'dummy_access_token',
        'id_token': 'dummy_id_token',
        'email': 'nonexistent@example.com'
    }

    def fake_exchange_code_for_tokens(code, client_id, client_secret, redirect_uri):
        return fake_tokens

    monkeypatch.setattr('tst_auth_svc.routers.google_oauth.exchange_code_for_tokens', fake_exchange_code_for_tokens)

    response = client.get('/google-callback', params={'code': 'valid_code'})
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    data = response.json()
    assert 'User not found' in data.get('detail', '')
