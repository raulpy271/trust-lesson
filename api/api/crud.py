from uuid import UUID
from http import HTTPStatus

from sqlalchemy import select
from pydantic import BaseModel
from fastapi import APIRouter, HTTPException

from api.models import Base, Session
from api.auth import LoggedUserId, User


def crud_router(
    model: type[Base],
    dtos: dict[str, type[BaseModel]],
    name: None | str = None,
    authorizations: dict = {},
    tags: list = [],
    methods: list = ["create", "list", "put", "delete"],
):
    name = name or model.__name__.lower()
    router = APIRouter(prefix="/" + name, tags=(tags or [name]))
    default_dto = dtos.get("default", dict)
    create_dto = dtos.get("create", default_dto)
    update_dto = dtos.get("update", default_dto)
    default_auth = authorizations.get("default")
    create_auth = authorizations.get("create", default_auth)
    list_auth = authorizations.get("list", default_auth)
    update_auth = authorizations.get("update", default_auth)
    delete_auth = authorizations.get("delete", default_auth)

    if "create" in methods:

        @router.post("/", status_code=HTTPStatus.CREATED)
        def create(data: create_dto, user_id: LoggedUserId):
            with Session() as session:
                if create_auth:
                    user = session.get(User, user_id)
                    if not create_auth(data, user, None):
                        raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED)
                obj = model(**data.model_dump())
                session.add(obj)
                session.commit()
                obj_res = obj.to_dict()
            return obj_res

    if "list" in methods:

        @router.get("/")
        def _list(user_id: LoggedUserId):
            with Session() as session:
                if list_auth:
                    user = session.get(User, user_id)
                    if not list_auth(None, user, None):
                        raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED)
                objs = session.scalars(select(model)).all()
                obj_res = [obj.to_dict() for obj in objs]
            return obj_res

    if "put" in methods:

        @router.put("/{resource_id}")
        def put(data: update_dto, resource_id: UUID, user_id: LoggedUserId):
            with Session() as session:
                if update_auth:
                    user = session.get(User, user_id)
                    if not update_auth(data, user, resource_id):
                        raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED)
                obj = session.get(model, resource_id)
                if obj:
                    for key, value in data.model_dump().items():
                        setattr(obj, key, value)
                    session.add(obj)
                    session.commit()
                    session.refresh(obj)
                    obj_res = obj.to_dict()
                else:
                    raise HTTPException(status_code=HTTPStatus.NOT_FOUND)
            return obj_res

    if "delete" in methods:

        @router.delete("/{resource_id}")
        def delete(resource_id: UUID, user_id: LoggedUserId):
            with Session() as session:
                if delete_auth:
                    user = session.get(User, user_id)
                    if not delete_auth(None, user, resource_id):
                        raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED)
                obj = session.get(model, resource_id)
                if obj:
                    session.delete(obj)
                    session.commit()
                else:
                    raise HTTPException(status_code=HTTPStatus.NOT_FOUND)

    return router
