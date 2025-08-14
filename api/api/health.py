import asyncio
from http import HTTPStatus

from sqlalchemy import select
from sqlalchemy import exc
from redis.exceptions import RedisError
from azure.core.exceptions import AzureError

from api import redis
from api.models import Session, User
from api.azure.storage import get_container_image
from api.dto import HealthOut


async def health(checks=["database", "redis", "storage"]):
    result = HealthOut()
    status_code = HTTPStatus.OK
    try:
        if "database" in checks:
            with Session() as session:
                session.scalars(select(User)).first()
            result.database_healthy = True
        else:
            result.database_error = "Not checked"
    except (exc.DisconnectionError, exc.OperationalError) as e:
        result.database_healthy = False
        result.database_error = str(e)
        status_code = HTTPStatus.INTERNAL_SERVER_ERROR
    try:
        if "redis" in checks:
            client = redis.get_default_client()
            client.info()
            result.redis_healthy = True
        else:
            result.redis_error = "Not checked"
    except RedisError as e:
        result.redis_healthy = False
        result.redis_error = str(e)
        status_code = HTTPStatus.INTERNAL_SERVER_ERROR
    try:
        if "storage" in checks:
            async with asyncio.timeout(10):
                container = get_container_image()
                await container.exists(timeout=1)
            result.storage_healthy = True
        else:
            result.storage_error = "Not checked"
    except (TimeoutError, AzureError) as e:
        result.storage_healthy = False
        result.storage_error = (
            str(e)
            if isinstance(e, AzureError)
            else "Timeout when trying to authenticate to Azure"
        )
        status_code = HTTPStatus.INTERNAL_SERVER_ERROR
    return result, status_code
