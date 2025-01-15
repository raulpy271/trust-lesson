
import mimesis
import pytest

from api import models
from api.auth import create_hash_salt

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

@pytest.fixture
def lesson(session):
    lesson = models.Lesson()
    session.add(lesson)
    session.commit()
    return lesson

