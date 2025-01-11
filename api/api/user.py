
from http import HTTPStatus
from typing import Annotated

from sqlalchemy import select
from fastapi import APIRouter, Depends

from api import dto
from api.models import Session, User
from api.auth import create_hash_salt, get_user_id

router = APIRouter(
    prefix="/user",
    tags=["user"]
)

@router.post("/create", status_code=HTTPStatus.CREATED)
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

@router.get("/me")
def me(user_id: Annotated[str, Depends(get_user_id)]):
    with Session() as session:
        u = session.scalars(select(User).where(User.id == user_id)).one()
    return u.to_dict()

