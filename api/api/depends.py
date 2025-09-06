from typing import Annotated
from http import HTTPStatus
from uuid import UUID

from fastapi import HTTPException, Request, Depends

from api.redis import get_default_client, hgetall_str
from api.models import AsyncSession


def get_user_id(request: Request):
    if request.state.logged:
        redis = get_default_client()
        mapping = hgetall_str(redis, request.state.token)
        if mapping and mapping.get("id"):
            return UUID(mapping["id"])
    raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED)


async def create_async_session_dep(request: Request):
    async with AsyncSession() as session:
        yield session


LoggedUserId = Annotated[UUID, Depends(get_user_id)]
SessionDep = Annotated[AsyncSession, Depends(create_async_session_dep)]
