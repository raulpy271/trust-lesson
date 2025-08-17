from dotenv import load_dotenv

load_dotenv("testing.env")

import mimesis
from sqlalchemy.pool import StaticPool
from sqlmodel import create_engine, SQLModel

import pytest

from api import models, settings
from api.auth import create_hash_salt


@pytest.fixture
def session():
    models._engine = create_engine(
        settings.DB_URL, connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    SQLModel.metadata.create_all(models._engine)
    with models.Session() as s:
        yield s


@pytest.fixture
def user_password(session):
    person = mimesis.Person()
    password = person.password()

    phash, salt = create_hash_salt(password)
    u = models.User(
        username=person.username(),
        fullname=person.full_name(),
        email=person.email(),
        role=models.UserRole.STUDANT,
        password_hash=phash,
        password_salt=salt,
    )
    session.add(u)
    session.commit()
    return (u, password)
