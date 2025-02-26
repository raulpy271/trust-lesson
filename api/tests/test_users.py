from hashlib import scrypt
from http import HTTPStatus

import mimesis
from sqlalchemy import select

from api import settings
from api.models import User


def test_create(session, client, token):
    person = mimesis.Person()
    user = {
        "username": person.username(),
        "fullname": person.full_name(),
        "email": person.email(),
        "password": person.password(),
    }
    resp = client.post("logged/user/create", json=user, auth=token)
    assert resp.status_code == HTTPStatus.CREATED
    u = session.scalars(select(User).where(User.username == user["username"])).one()
    assert u.fullname == user["fullname"]
    assert u.email == user["email"]
    phash = scrypt(
        user["password"].encode("utf-8"),
        salt=u.password_salt.encode("utf-8"),
        **settings.SCRYPT_SETTINGS,
    )
    assert u.password_hash == phash.hex()
