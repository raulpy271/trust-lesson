
from fastapi import APIRouter

from sqlalchemy import text

from api import redis
from api.models import Session

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


@router.get("/")
def hello_world():
    return "<p>Hello, World!</p>"

