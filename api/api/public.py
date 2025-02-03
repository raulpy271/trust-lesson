
from uuid import uuid4

from fastapi import APIRouter
from sqlalchemy import text

from api import redis
from api.models import Session
from api.aws import get_container_image

router = APIRouter(
    prefix="/public",
    tags=["public"]
)

@router.get("/test_db")
def test_db():
    with Session() as session:
        result = session.connection().execute(text("select version() as v"))
        return list(result)[0][0]

@router.get("/test_redis")
def test_redis():
    client = redis.get_default_client()
    client.set('test', 'hello from redis!')
    return client.get('test')

@router.get("/test_storage")
def test_storage():
    container = get_container_image()
    filename = f"{uuid4()}.txt"
    container.upload_blob(filename, "Hello World from storage", encoding="utf-8")
    stream = container.download_blob(filename, encoding="utf-8")
    return stream.readall()

@router.get("/")
def hello_world():
    return "<p>Hello, World!</p>"

