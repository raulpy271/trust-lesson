
from time import sleep
from datetime import datetime, timedelta
from http import HTTPStatus

from werkzeug.datastructures import Authorization
import pytest
import jwt

from api import settings
from tests.conftest import authenticate

def test_login_correct_password(user_password, client, redis):
    user, password = user_password
    start_expiration = datetime.now()
    end_expiration = datetime.now() + timedelta(seconds=settings.TOKEN_EXP + 1)
    resp = client.post("auth/login", json={"email": user.email, "password": password})
    assert resp.status_code == HTTPStatus.NO_CONTENT
    assert resp.headers.get('Token')
    assert resp.headers.get('Token-Expiration')
    assert jwt.decode(
        resp.headers.get('Token'),
        user.password_hash,
        issuer=settings.JWT_ISSUER,
        audience=user.email,
        algorithms=[settings.JWT_ALGORITHM])
    expiration = datetime.fromtimestamp(int(resp.headers.get('Token-Expiration')))
    assert start_expiration < expiration
    assert expiration < end_expiration

def test_login_wrong_password(user_password, client, redis):
    user, password = user_password
    resp = client.post("auth/login", json={"email": user.email, "password": password + "000"})
    assert resp.status_code == HTTPStatus.UNAUTHORIZED
    assert not resp.headers.get('Token')
    assert not resp.headers.get('Token-Expiration')

def test_login_wrong_email(user_password, client, redis):
    user, password = user_password
    resp = client.post("auth/login", json={"email": "000" + user.email, "password": password})
    assert resp.status_code == HTTPStatus.UNAUTHORIZED
    assert not resp.headers.get('Token')
    assert not resp.headers.get('Token-Expiration')

@pytest.mark.parametrize("path,method,data,json", [
    ("create", "POST", None, {}),
    ("me", "GET", None, {}),
])
def test_views_that_require_login(client, redis, user_password, path, method, data, json):
    user, password = user_password
    resp = client.open(path, method=method, data=data, json=json)
    assert resp.status_code == HTTPStatus.UNAUTHORIZED
    t = authenticate(client, user, password)
    resp = client.open(path, method=method, data=data, json=json, auth=t)
    assert resp.status_code != HTTPStatus.UNAUTHORIZED

@pytest.mark.slow
def test_expiration_token(monkeypatch, client, redis, user_password):
    exp = 1
    monkeypatch.setattr(settings, "TOKEN_EXP", exp)
    user, password = user_password
    t = authenticate(client, user, password)
    sleep(exp + 0.2)
    resp = client.get("me", auth=t)
    assert resp.status_code == HTTPStatus.UNAUTHORIZED

@pytest.mark.slow
def test_regenerate_new_token(monkeypatch, client, redis, user_password):
    monkeypatch.setattr(settings, "TOKEN_EXP", 3)
    monkeypatch.setattr(settings, "TOKEN_REGENERATE", 2)
    user, password = user_password
    t = authenticate(client, user, password)
    resp = client.get("me", auth=t)
    datetime_exp = datetime.fromtimestamp(int(resp.headers['Token-Expiration']))
    assert resp.status_code == HTTPStatus.OK
    assert resp.headers['Token'] == t.token
    assert datetime.now() < datetime_exp
    sleep(2)
    resp = client.get("me", auth=t)
    assert resp.status_code == HTTPStatus.OK
    assert resp.headers['Token'] != t.token
    assert datetime_exp < datetime.fromtimestamp(int(resp.headers['Token-Expiration']))

@pytest.mark.slow
def test_invalidate_old_token(monkeypatch, client, redis, user_password):
    monkeypatch.setattr(settings, "TOKEN_EXP", 3)
    monkeypatch.setattr(settings, "TOKEN_REGENERATE", 2)
    user, password = user_password
    t = authenticate(client, user, password)
    sleep(2)
    resp = client.get("me", auth=t)
    assert resp.status_code == HTTPStatus.OK
    assert resp.headers['Token'] != t.token
    new_token = Authorization("bearer", token=resp.headers['Token'])
    resp = client.get("me", auth=t)
    assert resp.status_code == HTTPStatus.UNAUTHORIZED
    resp = client.get("me", auth=new_token)
    assert resp.status_code == HTTPStatus.OK

