import os
import uuid
import logging

from fastapi import APIRouter, Request, HTTPException, status, Depends
from fastapi.responses import RedirectResponse

from sqlalchemy.orm import Session

from tst_auth_svc.models.session import SessionToken
from tst_auth_svc.models.base import get_db
from tst_auth_svc.models.user import User

# Import functions from the google_oauth_client module
from tst_auth_svc.google_oauth_client import generate_auth_url, exchange_code_for_tokens

router = APIRouter()


@router.get('/google-login')
async def google_login() -> RedirectResponse:
    """
    Initiates Google OAuth2 login by generating an authentication URL using client configuration
    from environment variables and redirects the user.
    """
    try:
        client_id = os.getenv('GOOGLE_CLIENT_ID')
        client_secret = os.getenv('GOOGLE_CLIENT_SECRET')
        redirect_uri = os.getenv('GOOGLE_REDIRECT_URI')

        if not all([client_id, client_secret, redirect_uri]):
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail='Google OAuth configuration is incomplete.')

        # Generate the Google authentication URL using the external module
        auth_url = generate_auth_url(client_id, redirect_uri)
        return RedirectResponse(url=auth_url)
    except Exception as e:
        logging.error(e, exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail='Failed to initiate Google OAuth login process.')


@router.get('/google-callback')
async def google_callback(request: Request, db: Session = Depends(get_db)):
    """
    Handles the OAuth2 callback by exchanging the authorization code for tokens, validating
    the token response, and creating a user session upon successful authentication.
    """
    try:
        # Retrieve the authorization code from query parameters
        code = request.query_params.get('code')
        if not code:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail='Authorization code is missing.')

        client_id = os.getenv('GOOGLE_CLIENT_ID')
        client_secret = os.getenv('GOOGLE_CLIENT_SECRET')
        redirect_uri = os.getenv('GOOGLE_REDIRECT_URI')

        if not all([client_id, client_secret, redirect_uri]):
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail='Google OAuth configuration is incomplete.')

        # Exchange the authorization code for tokens
        try:
            token_response = exchange_code_for_tokens(code, client_id, client_secret, redirect_uri)
        except Exception as e:
            logging.error(e, exc_info=True)
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail='Failed to exchange code for tokens.')

        # Validate token response
        access_token = token_response.get('access_token')
        id_token = token_response.get('id_token')
        email = token_response.get('email')  # Assuming the token response includes user's email

        if not (access_token and id_token and email):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail='Invalid token exchange response.')

        # Retrieve the user from the database using the email from token response
        user = db.query(User).filter(User.email == email).first()
        if not user:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail='User not found for the provided Google account.')

        # Generate a secure session token
        session_token_str = str(uuid.uuid4())
        new_session = SessionToken(user_id=user.id, session_token=session_token_str)

        try:
            db.add(new_session)
            db.commit()
        except Exception as e:
            logging.error(e, exc_info=True)
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail='Failed to create user session.')

        return {'message': 'Google OAuth login successful', 'session_token': session_token_str}
    except HTTPException as e:
        raise e
    except Exception as e:
        logging.error(e, exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail='An error occurred during Google OAuth callback.')
