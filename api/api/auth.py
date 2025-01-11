
from typing import Annotated
from datetime import datetime
from hashlib import scrypt
from secrets import token_hex
from http import HTTPStatus
from uuid import UUID
import re

import jwt
from jwt.exceptions import InvalidTokenError
from sqlalchemy import select
from fastapi import APIRouter, Response, Header, HTTPException, Request
from starlette.middleware.base import BaseHTTPMiddleware

from api import settings
from api import dto
from api.models import Session, User
from api.redis import get_default_client, hgetall_str

router = APIRouter(
    prefix="/auth",
    tags=["auth"]
)

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

class CheckAuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        if self.should_be_logged(request):
            logged, token, mapping = self.verify_token(request)
            request.state.logged = logged
            request.state.token = token
            if logged:
                response = await call_next(request)
                self.add_logged_headers(response, token, mapping)
            else:
                response = Response(status_code=HTTPStatus.UNAUTHORIZED)
        else:
            response = await call_next(request)
        return response

    def should_be_logged(self, request):
        return "/logged/" in request.url.path

    def verify_token(self, request):
        authorization = request.headers.get('Authorization')
        if authorization:
            token = parse_bearer(authorization)
            if token:
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
                        raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED)
                    except:
                        raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR)
                    return True, token, mapping
        return False, None, None

    def add_logged_headers(self, response, token, mapping):
        redis = get_default_client()
        exp_s = redis.ttl(token)
        exp_ts = int(datetime.now().timestamp() + exp_s)
        if exp_s <= settings.TOKEN_REGENERATE:
            token, exp_ts = generate_new_token(token, mapping)
        response.headers['Token'] = token
        response.headers['Token-Expiration'] = str(exp_ts)

def get_user_id(request: Request):
    if request.state.logged:
        redis = get_default_client()
        mapping = hgetall_str(redis, request.state.token)
        if mapping and mapping.get('id'):
            return UUID(mapping['id'])
    raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED)

@router.post("/login")
def login(response: Response, data: dto.LoginIn):
    with Session() as session:
        user = session.scalars(select(User).where(User.email == data.email)).one_or_none()
        if user and check_hash(user, data.password):
            token, expiration = create_token(user)
            response.headers.update({'Token': token, 'Token-Expiration': str(expiration)})
            response.status_code = HTTPStatus.NO_CONTENT
            return {}
        else:
            response.status_code = HTTPStatus.UNAUTHORIZED
            return {}

@router.post("/logout")
def logout(response: Response, authorization: Annotated[str | None, Header()] = None):
    if authorization:
        token = parse_bearer(authorization)
        if token:
            redis = get_default_client()
            deleted = redis.delete(token)
            if deleted:
                response.status_code = HTTPStatus.OK
                return response
    response.status_code = HTTPStatus.BAD_REQUEST
    return response

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

def parse_bearer(token: str) -> str | None:
    match = re.fullmatch(r"Bearer\s+(\w+\.\w+\.\S+)", token)
    if match:
        return match.group(1)
