
from dotenv import load_dotenv
load_dotenv("testing.env")

from http import HTTPStatus

import pytest
import fakeredis
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from werkzeug.datastructures import Authorization

import api.redis
from api import models, settings
from api.auth import create_hash_salt
from api import create_app

@pytest.fixture()
def general(monkeypatch):
    monkeypatch.setattr(settings, "TOKEN_EXP", 10)
    monkeypatch.setattr(settings, "SCRYPT_SETTINGS", {'n': 2 ** 6, 'r': 8, 'p': 1})

@pytest.fixture
def session():
    models._engine = create_engine(settings.DB_URL)
    models._session = sessionmaker(models._engine)
    models.Base.metadata.create_all(models._engine)
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
    return app.test_client()

@pytest.fixture
def user_password(session):
    password = "hello1234"
    phash, salt = create_hash_salt(password)
    u = models.User(
        username="Raul",
        fullname="Jose Raul",
        email="raul@gmail.com",
        role=models.UserRole.STUDANT,
        password_hash=phash,
        password_salt=salt,
    )
    session.add(u)
    session.commit()
    return (u, password)

def authenticate(client, user, password):
    resp = client.post("auth/login", json={"email": user.email, "password": password})
    assert resp.headers.get('Token')
    return Authorization("bearer", token=resp.headers['Token'])

@pytest.fixture
def token(client, redis, user_password):
    user, password = user_password
    return authenticate(client, user, password)


