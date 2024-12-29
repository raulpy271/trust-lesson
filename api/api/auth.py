
from functools import wraps
from datetime import datetime
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
from api.redis import get_default_client, hgetall_str

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
    pipe = redis.pipeline()
    mapping = {"id": str(user.id), "email": user.email, "password_hash": user.password_hash}
    pipe.hset(token, mapping=mapping)
    pipe.expire(token, settings.TOKEN_EXP)
    pipe.execute()
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

def require_login(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if request.authorization and request.authorization.type == "bearer":
            token = str(request.authorization.token)
            redis = get_default_client()
            mapping = hgetall_str(redis, token)
            if mapping and mapping.get('password_hash') and mapping.get('email'):
                try:
                    jwt.decode(
                        token,
                        mapping['password_hash'],
                        issuer=settings.JWT_ISSUER,
                        audience=mapping['email'],
                        algorithms=[settings.JWT_ALGORITHM])
                except Exception as e:
                    return {}, HTTPStatus.UNAUTHORIZED
                resp = f(*args, **kwargs)
                expiration = redis.ttl(token)
                return add_headers_to_response(resp, {'Token': token, 'Token-Expiration': expiration})
            else:
                return {}, HTTPStatus.UNAUTHORIZED
        else:
            return {}, HTTPStatus.UNAUTHORIZED
    return wrapper

def add_headers_to_response(response, headers):
    return (response[0], response[1], headers)

