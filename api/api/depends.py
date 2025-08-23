from typing import Annotated
from http import HTTPStatus
from uuid import UUID

from fastapi import HTTPException, Request, Depends

from api.redis import get_default_client, hgetall_str
from api.models import Session


def get_user_id(request: Request):
    if request.state.logged:
        redis = get_default_client()
        mapping = hgetall_str(redis, request.state.token)
        if mapping and mapping.get("id"):
            return UUID(mapping["id"])
    raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED)


def create_session_dep(request: Request):
    with Session() as session:
        yield session


LoggedUserId = Annotated[str, Depends(get_user_id)]
SessionDep = Annotated[Session, Depends(create_session_dep)]
