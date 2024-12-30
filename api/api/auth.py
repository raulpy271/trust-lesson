
from uuid import UUID
from functools import wraps
from datetime import datetime
from hashlib import scrypt
from secrets import token_hex
from http import HTTPStatus

import jwt
from jwt.exceptions import InvalidTokenError
from sqlalchemy import select
from flask import (
    Blueprint,
    request,
    g)

from api import settings
from api.models import Session, User
from api.utils import add_headers_to_response
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
        'id': str(user.id),
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
            if mapping and mapping.get('password_hash') and mapping.get('email') and mapping.get('id'):
                try:
                    jwt.decode(
                        token,
                        mapping['password_hash'],
                        issuer=settings.JWT_ISSUER,
                        audience=mapping['email'],
                        algorithms=[settings.JWT_ALGORITHM])
                except InvalidTokenError:
                    return {}, HTTPStatus.UNAUTHORIZED
                except:
                    return {}, HTTPStatus.INTERNAL_SERVER_ERROR
                g.user_id = UUID(mapping['id'])
                resp = f(*args, **kwargs)
                exp_s = redis.ttl(token)
                exp_ts = int(datetime.now().timestamp() + exp_s)
                if exp_s <= settings.TOKEN_REGENERATE:
                    token, exp_ts = generate_new_token(token, mapping)
                return add_headers_to_response(resp, {'Token': token, 'Token-Expiration': exp_ts})
            else:
                return {}, HTTPStatus.UNAUTHORIZED
        else:
            return {}, HTTPStatus.UNAUTHORIZED
    return wrapper

def generate_new_token(old_token, mapping):
    exp = int(datetime.now().timestamp() + settings.TOKEN_EXP)
    data = {
        'email': mapping['email'],
        'id': mapping['id'],
        'exp': exp,
        'iss': settings.JWT_ISSUER,
        'aud': mapping['email'],
    }
    token = jwt.encode(data, mapping['password_hash'], algorithm=settings.JWT_ALGORITHM)
    redis = get_default_client()
    pipe = redis.pipeline()
    pipe.delete(old_token)
    pipe.hset(token, mapping=mapping)
    pipe.expire(token, settings.TOKEN_EXP)
    pipe.execute()
    return token, exp

