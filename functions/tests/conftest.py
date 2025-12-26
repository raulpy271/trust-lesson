from dotenv import load_dotenv

load_dotenv("testing.env")

import mimesis
from sqlalchemy.pool import StaticPool
from sqlmodel import SQLModel
from sqlalchemy.ext.asyncio import create_async_engine

import pytest

from api import models, settings
from api.auth import create_hash_salt


@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest.fixture
async def session(anyio_backend):
    models._async_engine = create_async_engine(
        settings.DB_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        echo=False,
    )
    async with models._async_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
    async with models.AsyncSession() as s:
        yield s


@pytest.fixture
async def user_password(session):
    person = mimesis.Person()
    password = person.password()

    phash, salt = create_hash_salt(password)
    u = models.User(
        username=person.username(),
        fullname=person.full_name(),
        email=person.email(),
        role=models.UserRole.STUDENT,
        password_hash=phash,
        password_salt=salt,
    )
    session.add(u)
    await session.commit()
    return (u, password)
