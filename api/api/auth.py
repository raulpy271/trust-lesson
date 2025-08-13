from typing import Annotated
from datetime import datetime
from hashlib import scrypt
from secrets import token_hex
from http import HTTPStatus

import jwt
from sqlalchemy import select
from fastapi import APIRouter, Response, Header

from api import settings
from api import dto
from api.models import Session, User
from api.redis import get_default_client
from api.utils import parse_bearer

router = APIRouter(prefix="/auth", tags=["auth"])


def create_hash_salt(password):
    salt = token_hex()
    phash = scrypt(
        password.encode("utf-8"), salt=salt.encode("utf-8"), **settings.SCRYPT_SETTINGS
    )
    return phash.hex(), salt


def check_hash(user, password):
    phash = scrypt(
        password.encode("utf-8"),
        salt=user.password_salt.encode("utf-8"),
        **settings.SCRYPT_SETTINGS,
    )
    return phash.hex() == user.password_hash


def create_token(user):
    exp = int(datetime.now().timestamp() + settings.TOKEN_EXP)
    data = {
        "email": user.email,
        "id": str(user.id),
        "exp": exp,
        "iss": settings.JWT_ISSUER,
        "aud": user.email,
    }
    token = jwt.encode(data, user.password_hash, algorithm=settings.JWT_ALGORITHM)
    redis = get_default_client()
    pipe = redis.pipeline()
    mapping = {
        "id": str(user.id),
        "email": user.email,
        "password_hash": user.password_hash,
    }
    pipe.hset(token, mapping=mapping)
    pipe.expire(token, settings.TOKEN_EXP)
    pipe.execute()
    return token, exp


@router.post("/login")
def login(response: Response, data: dto.LoginIn):
    with Session() as session:
        user = session.scalars(
            select(User).where(User.email == data.email)
        ).one_or_none()
        if user and check_hash(user, data.password):
            token, expiration = create_token(user)
            response.headers.update(
                {"Token": token, "Token-Expiration": str(expiration)}
            )
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
        "email": mapping["email"],
        "id": mapping["id"],
        "exp": exp,
        "iss": settings.JWT_ISSUER,
        "aud": mapping["email"],
    }
    token = jwt.encode(data, mapping["password_hash"], algorithm=settings.JWT_ALGORITHM)
    redis = get_default_client()
    pipe = redis.pipeline()
    pipe.delete(old_token)
    pipe.hset(token, mapping=mapping)
    pipe.expire(token, settings.TOKEN_EXP)
    pipe.execute()
    return token, exp
