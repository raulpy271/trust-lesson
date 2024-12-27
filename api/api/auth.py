
from datetime import datetime, timedelta
from hashlib import scrypt
from secrets import token_hex
from http import HTTPStatus

import jwt
from sqlalchemy import select
from flask import (
    Blueprint,
    request)

from api import settings
from api.models import Session, User
from api.redis import get_default_client

bp = Blueprint('auth', __name__, url_prefix='/auth')

def create_hash_salt(password):
    salt = token_hex()
    phash = scrypt(
        password.encode('utf-8'),
        salt=salt.encode('utf-8'),
        **settings.SCRYPT_SETTINGS)
    return phash.hex(), salt

def check_hash(user, password):
    phash = scrypt(
        password.encode('utf-8'),
        salt=user.password_salt.encode('utf-8'),
        **settings.SCRYPT_SETTINGS)
    return phash.hex() == user.password_hash

def create_token(user):
    exp = int(datetime.now().timestamp() + settings.TOKEN_EXP)
    data = {
        'email': user.email,
        'username': user.username,
        'exp': exp,
        'iss': settings.JWT_ISSUER,
        'aud': user.email,
    }
    token = jwt.encode(data, user.password_hash, algorithm=settings.JWT_ALGORITHM)
    redis = get_default_client()
    redis.set(user.email, token, ex=settings.TOKEN_EXP)
    return token, exp

@bp.post("/login")
def login():
    data = request.get_json()
    email = data.pop('email')
    password = data.pop('password')
    with Session() as session:
        user = session.scalars(select(User).where(User.email == email)).one_or_none()
        if user and check_hash(user, password):
            token, expiration = create_token(user)
            return {}, HTTPStatus.NO_CONTENT, {'Token': token, 'Token-Expiration': expiration}
        else:
            return {}, HTTPStatus.UNAUTHORIZED


