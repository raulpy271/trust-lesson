from typing import Annotated
from http import HTTPStatus

from sqlmodel import select
from fastapi import APIRouter, Response, Header

from api import dto
from api.models import User
from api.auth import check_hash, create_token
from api.redis import get_default_client
from api.utils import parse_bearer
from api.depends import SessionDep


router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", summary="Do login and return token in response headers")
async def login(response: Response, data: dto.LoginIn, session: SessionDep):
    result = await session.exec(select(User).where(User.email == data.email))
    user = result.one_or_none()
    if user and check_hash(user, data.password):
        token, expiration = create_token(user)
        response.headers.update({"Token": token, "Token-Expiration": str(expiration)})
        response.status_code = HTTPStatus.NO_CONTENT
    else:
        response.status_code = HTTPStatus.UNAUTHORIZED


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
