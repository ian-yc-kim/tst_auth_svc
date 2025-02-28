from fastapi import FastAPI
from tst_auth_svc.models.base import get_db, get_secure_db

app = FastAPI(debug=True)

"""
Dependency Override Configuration:
The default database dependency 'get_db' is overridden with 'get_secure_db'.

get_secure_db is implemented as a generator function that yields a secure SQLAlchemy
Session instance. It includes enhanced error management: any exceptions during
session creation are caught, logged with detailed traceback (using logging.error), and
re-raised. This ensures that FastAPI's dependency injection correctly manages the
session lifecycle, including proper cleanup after each request.

Note: This override is applied only in the production environment. In tests, the dependency
may be further overridden via fixtures.
"""
app.dependency_overrides[get_db] = get_secure_db

# add routers
from tst_auth_svc.routers import registration
app.include_router(registration.router)

from tst_auth_svc.routers import login
app.include_router(login.router)

from tst_auth_svc.routers import password_reset
app.include_router(password_reset.router)

from tst_auth_svc.routers import password_update
app.include_router(password_update.router)

from tst_auth_svc.routers import logout
app.include_router(logout.router)

# Include the new Google OAuth router
from tst_auth_svc.routers import google_oauth
app.include_router(google_oauth.router)
