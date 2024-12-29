
from hashlib import scrypt
from http import HTTPStatus

from sqlalchemy import select

from api import settings
from api.models import User

def test_create(session, client, token):
    user = {
        'username': 'Raul 124',
        'fullname': 'Jose Raul',
        'email': 'raul@gmail.com',
        'password': 'hello_password',
    }
    resp = client.post("create", json=user, auth=token)
    assert resp.status_code == HTTPStatus.CREATED
    u = session.scalars(select(User).where(User.username == user['username'])).one()
    assert u.fullname == user['fullname']
    assert u.email == user['email']
    phash = scrypt(
        user['password'].encode('utf-8'),
        salt=u.password_salt.encode('utf-8'),
        **settings.SCRYPT_SETTINGS)
    assert u.password_hash == phash.hex()
