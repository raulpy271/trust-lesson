from uuid import uuid4


from fastapi import APIRouter, Response
from sqlalchemy import text

import api.health
from api import redis
from api.models import Session
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
    result, status_code = await api.health.health()
    response.status_code = status_code
    return result


@router.get("/")
def hello_world():
    return "<p>Hello, World!</p>"
