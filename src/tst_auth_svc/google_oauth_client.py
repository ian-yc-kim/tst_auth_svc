import logging

"""
This module provides a dummy implementation of Google OAuth2 related functions.
Note: This implementation is for development/testing purposes only.
For production, integrate with actual Google OAuth2 API calls and proper error handling.
"""

def generate_auth_url(client_id: str, redirect_uri: str, scope: str = None) -> str:
    """Generates a Google authentication URL for initiating the OAuth2 login process.
    
    Args:
        client_id (str): The Google OAuth2 client ID.
        redirect_uri (str): The URI to redirect to after authentication.
        scope (str, optional): The space-delimited OAuth2 scopes. Defaults to None.
    
    Returns:
        str: The URL to redirect the user for Google OAuth2 authentication.
    """
    base_url = "https://accounts.google.com/o/oauth2/auth"
    url = f"{base_url}?client_id={client_id}&redirect_uri={redirect_uri}&response_type=code"
    if scope:
        url += f"&scope={scope}"
    return url


def exchange_code_for_tokens(code: str, client_id: str, client_secret: str, redirect_uri: str) -> dict:
    """Exchanges an authorization code for access and ID tokens from Google.
    
    Note: This is a dummy implementation. In production, this function should
    make an HTTP request to Google's token endpoint and handle responses accordingly.

    Args:
        code (str): The authorization code returned by Google.
        client_id (str): The Google OAuth2 client ID.
        client_secret (str): The Google OAuth2 client secret.
        redirect_uri (str): The redirect URI used in the authentication request.

    Returns:
        dict: A dictionary containing 'access_token', 'id_token', and 'email'.
    
    Raises:
        Exception: If the provided code is invalid.
    """
    if code == "valid_code":
        return {
            "access_token": "dummy_access_token",
            "id_token": "dummy_id_token",
            "email": "testuser@example.com"
        }
    raise Exception("Invalid code")
