import re
from datetime import datetime
from hashlib import scrypt
from secrets import token_hex

import jwt

from api import settings
from api.redis import get_default_client


VALID_SIMBOLS = r"!^@#$%^&*()\-_=+?:"
UPPER_CASE_AND_LOWER_CASE_RE = re.compile(r"[a-z].*[A-Z]|[A-Z].*[a-z]")
DIGITS_AND_SIMBOLS = re.compile(rf"[0-9].*[{VALID_SIMBOLS}]|[{VALID_SIMBOLS}].*[0-9]")
VALID_CHARS = re.compile(rf"[a-zA-Z0-9{VALID_SIMBOLS}]{{10,25}}")


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


async def create_token(user):
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
    mapping = {
        "id": str(user.id),
        "email": user.email,
        "password_hash": user.password_hash,
    }
    async with redis.pipeline(transaction=True) as pipe:
        pipe.hset(token, mapping=mapping)
        pipe.expire(token, settings.TOKEN_EXP)
        await pipe.execute()
    return token, exp


async def generate_new_token(old_token, mapping):
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
    async with redis.pipeline(transaction=True) as pipe:
        pipe.delete(old_token)
        pipe.hset(token, mapping=mapping)
        pipe.expire(token, settings.TOKEN_EXP)
        await pipe.execute()
    return token, exp


def validate_password(password: str) -> bool:
    if (
        VALID_CHARS.fullmatch(password)
        and UPPER_CASE_AND_LOWER_CASE_RE.search(password)
        and DIGITS_AND_SIMBOLS.search(password)
    ):
        return True
    else:
        return False
