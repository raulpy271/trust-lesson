from dotenv import load_dotenv

load_dotenv("testing.env")

import pytest
import fakeredis
from sqlmodel import SQLModel, create_engine
from fastapi.testclient import TestClient
from sqlalchemy.pool import StaticPool

import api.redis
from api import models, settings
from api.app import create_app
from tests.utils import authenticate

pytest_plugins = [
    "tests.factories",
]


@pytest.fixture()
def general(monkeypatch):
    monkeypatch.setattr(settings, "TOKEN_EXP", 10)
    monkeypatch.setattr(settings, "TOKEN_REGENERATE", 2)
    monkeypatch.setattr(settings, "SCRYPT_SETTINGS", {"n": 2**6, "r": 8, "p": 1})


@pytest.fixture
def session():
    models._engine = create_engine(
        settings.DB_URL, connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    SQLModel.metadata.create_all(models._engine)
    with models.Session() as s:
        yield s


@pytest.fixture
def redis():
    api.redis._redis = fakeredis.FakeRedis()
    return api.redis._redis


@pytest.fixture
def app():
    """Create and configure a new app instance for each test."""
    app = create_app()
    return app


@pytest.fixture
def client(app):
    """A test client for the app."""
    return TestClient(app)


@pytest.fixture
def token(client, redis, user_password):
    user, password = user_password
    return authenticate(client, user, password)


@pytest.fixture
def container():
    class ContainerMock:
        async def upload_blob(self, key, *args, **kwargs):
            self.key = key

    return ContainerMock()
