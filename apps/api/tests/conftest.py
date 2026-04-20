from __future__ import annotations

import sys

import pytest

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import os

os.environ["DATABASE_URL"] = "sqlite://"
os.environ["SECRET_KEY"] = "test-secret"
os.environ["WEB_BASE_URL"] = "http://localhost:5173"
os.environ["GOOGLE_CLIENT_ID"] = "google-client-id"
os.environ["GOOGLE_CLIENT_SECRET"] = "google-client-secret"
os.environ["GOOGLE_REDIRECT_URI"] = "http://localhost:8000/api/v1/auth/google/callback"
os.environ["FACEBOOK_CLIENT_ID"] = "facebook-client-id"
os.environ["FACEBOOK_CLIENT_SECRET"] = "facebook-client-secret"
os.environ["FACEBOOK_REDIRECT_URI"] = "http://localhost:8000/api/v1/auth/facebook/callback"

from fastapi.testclient import TestClient

from app.db.session import create_all, engine
from app.main import create_app
from app.models.base import Base


@pytest.fixture(autouse=True)
def reset_database():
    Base.metadata.drop_all(bind=engine)
    create_all()
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client():
    app = create_app()
    with TestClient(app) as test_client:
        yield test_client
