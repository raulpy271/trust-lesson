from datetime import datetime
from hashlib import scrypt
from secrets import token_hex

import jwt

from api import settings
from api.redis import get_default_client


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
