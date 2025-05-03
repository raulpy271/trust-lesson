import asyncio
from http import HTTPStatus

from sqlalchemy import select
from sqlalchemy import exc
from redis.exceptions import RedisError
from azure.core.exceptions import AzureError

from api import redis
from api.models import Session, User
from api import azure
from api.dto import HealthOut


async def health():
    result = HealthOut()
    status_code = HTTPStatus.OK
    try:
        with Session() as session:
            session.scalars(select(User)).one_or_none()
    except (exc.DisconnectionError, exc.OperationalError) as e:
        result.database_healthy = False
        result.database_error = str(e)
        status_code = HTTPStatus.INTERNAL_SERVER_ERROR
    try:
        client = redis.get_default_client()
        client.info()
    except RedisError as e:
        result.redis_healthy = False
        result.redis_error = str(e)
        status_code = HTTPStatus.INTERNAL_SERVER_ERROR
    try:
        async with asyncio.timeout(10):
            container = azure.get_container_image()
            await container.exists(timeout=1)
    except (TimeoutError, AzureError) as e:
        result.storage_healthy = False
        result.storage_error = (
            str(e)
            if isinstance(e, AzureError)
            else "Timeout when trying to authenticate to Azure"
        )
        status_code = HTTPStatus.INTERNAL_SERVER_ERROR
    return result, status_code
