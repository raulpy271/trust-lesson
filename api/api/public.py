import asyncio
from http import HTTPStatus
from uuid import uuid4


from fastapi import APIRouter, Response
from sqlalchemy import select, text
from sqlalchemy import exc
from redis.exceptions import RedisError
from azure.core.exceptions import AzureError

from api import redis
from api.models import Session, User
from api import azure
from api.dto import HealthOut

router = APIRouter(prefix="/public", tags=["public"])


@router.get("/test_db")
def test_db():
    with Session() as session:
        result = session.connection().execute(text("select version() as v"))
        return list(result)[0][0]


@router.get("/test_redis")
def test_redis():
    client = redis.get_default_client()
    client.set("test", "hello from redis!")
    return client.get("test")


@router.get("/test_storage")
async def test_storage():
    container = azure.get_container_image()
    filename = f"{uuid4()}.txt"
    await container.upload_blob(filename, "Hello World from storage", encoding="utf-8")
    stream = await container.download_blob(filename, encoding="utf-8")
    return await stream.readall()


@router.get("/health", response_model=HealthOut)
async def health(response: Response):
    result = HealthOut()
    try:
        with Session() as session:
            session.scalars(select(User)).one_or_none()
    except (exc.DisconnectionError, exc.OperationalError) as e:
        result.database_healthy = False
        result.database_error = str(e)
        response.status_code = HTTPStatus.INTERNAL_SERVER_ERROR
    try:
        client = redis.get_default_client()
        client.info()
    except RedisError as e:
        result.redis_healthy = False
        result.redis_error = str(e)
        response.status_code = HTTPStatus.INTERNAL_SERVER_ERROR
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
        response.status_code = HTTPStatus.INTERNAL_SERVER_ERROR
    return result


@router.get("/")
def hello_world():
    return "<p>Hello, World!</p>"
