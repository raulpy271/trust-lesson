from typing import Annotated
from http import HTTPStatus
from uuid import UUID

from fastapi import HTTPException, Request, Depends

from api.redis import get_default_client, hgetall_str


def get_user_id(request: Request):
    if request.state.logged:
        redis = get_default_client()
        mapping = hgetall_str(redis, request.state.token)
        if mapping and mapping.get("id"):
            return UUID(mapping["id"])
    raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED)


LoggedUserId = Annotated[str, Depends(get_user_id)]
