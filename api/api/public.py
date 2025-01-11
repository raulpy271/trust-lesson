
from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends

from sqlalchemy import (
    text,
    select)

from api import redis
from api.models import User
from api.models import Session
from api import dto
from api.auth import create_hash_salt, get_user_id

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
    client.set('test', 'hello')
    return client.get('test')

@router.post("/logged/create", status_code=HTTPStatus.CREATED)
def create(data: dto.CreateUserIn):
    with Session() as session:
        data = data.model_dump()
        password = data.pop('password')
        phash, salt = create_hash_salt(password)
        data['password_hash'] = phash
        data['password_salt'] = salt
        user = User(**data)
        session.add(user)
        session.commit()
    return {}

@router.get("/logged/me")
def me(user_id: Annotated[str, Depends(get_user_id)]):
    with Session() as session:
        u = session.scalars(select(User).where(User.id == user_id)).one()
    return u.to_dict()


@router.get("/")
def hello_world():
    return "<p>Hello, World!</p>"

