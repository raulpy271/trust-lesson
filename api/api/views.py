
from hashlib import scrypt
from secrets import token_hex
from http import HTTPStatus

from flask import (
    Blueprint,
    request)
from sqlalchemy import text

from api import settings
from api import redis
from api.models import User
from api.models import Session, Base

bp = Blueprint('api', __name__)

@bp.route("/test_db")
def test_db():
    with Session() as session:
        result = session.connection().execute(text("select version() as v"))
        return list(result)[0][0]

@bp.route("/test_redis")
def test_redis():
    client = redis.get_default_client()
    client.set('test', 'hello')
    return client.get('test')

def create_hash_salt(password):
    salt = token_hex()
    phash = scrypt(
        password.encode('utf-8'),
        salt=salt.encode('utf-8'),
        **settings.SCRYPT_SETTINGS)
    return phash.hex(), salt

@bp.post("/create")
def create():
    with Session() as session:
        data = request.get_json()
        password = data.pop('password')
        phash, salt = create_hash_salt(password)
        data['password_hash'] = phash
        data['password_salt'] = salt
        user = User(**data)
        session.add(user)
        session.commit()
    return {}, HTTPStatus.CREATED

@bp.route("/")
def hello_world():
    return "<p>Hello, World!</p>"

