from typing import Optional
from uuid import UUID
from http import HTTPStatus

from sqlmodel import select
from pydantic import BaseModel
from fastapi import APIRouter, HTTPException

from api.models import User
from api.models.base import Base
from api.depends import LoggedUserId, SessionDep


def crud_router(
    model: type[Base],
    dtos: dict[str, type[BaseModel]],
    name: None | str = None,
    authorizations: dict = {},
    tags: list = [],
    methods: list = ["get", "create", "list", "put", "delete"],
    router: Optional[APIRouter] = None,
    response_model_relationship: dict[str, dict | set] = {},
):
    name = name or model.__name__.lower()
    router: APIRouter = router or APIRouter(prefix="/" + name, tags=(tags or [name]))
    default_dto = dtos.get("default", dict)
    create_dto = dtos.get("create", default_dto)
    update_dto = dtos.get("update", default_dto)
    delete_dto = dtos.get("delete", default_dto)
    default_auth = authorizations.get("default")
    get_auth = authorizations.get("get", default_auth)
    create_auth = authorizations.get("create", default_auth)
    list_auth = authorizations.get("list", default_auth)
    update_auth = authorizations.get("update", default_auth)
    delete_auth = authorizations.get("delete", default_auth)
    default_relationship = response_model_relationship.get("default", {})
    get_relationship = response_model_relationship.get("get", default_relationship)
    create_relationship = response_model_relationship.get(
        "create", default_relationship
    )
    list_relationship = response_model_relationship.get("list", default_relationship)
    update_relationship = response_model_relationship.get(
        "update", default_relationship
    )

    if "create" in methods:

        @router.post(
            "/",
            status_code=HTTPStatus.CREATED,
            response_model=model.response_model(create_relationship),
        )
        def create(data: create_dto, user_id: LoggedUserId, session: SessionDep):
            if create_auth:
                user = session.get(User, user_id)
                if not create_auth(data, user, None):
                    raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED)
            obj = model(**data.model_dump())
            session.add(obj)
            session.commit()
            session.refresh(obj)
            return obj

    if "list" in methods:

        @router.get("/", response_model=list[model.response_model(list_relationship)])
        def _list(user_id: LoggedUserId, session: SessionDep):
            if list_auth:
                user = session.get(User, user_id)
                if not list_auth(None, user, None):
                    raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED)
            objs = session.exec(select(model)).all()
            return objs

    if "get" in methods:

        @router.get(
            "/{resource_id}", response_model=model.response_model(get_relationship)
        )
        def get(resource_id: UUID, user_id: LoggedUserId, session: SessionDep):
            if get_auth:
                user = session.get(User, user_id)
                if not get_auth(None, user, resource_id):
                    raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED)
            obj = session.get(model, resource_id)
            if obj:
                return obj
            else:
                raise HTTPException(status_code=HTTPStatus.NOT_FOUND)

    if "put" in methods:

        @router.put(
            "/{resource_id}", response_model=model.response_model(update_relationship)
        )
        def put(
            resource_id: UUID,
            data: update_dto,
            user_id: LoggedUserId,
            session: SessionDep,
        ):
            if update_auth:
                user = session.get(User, user_id)
                if not update_auth(data, user, resource_id):
                    raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED)
            obj = session.get(model, resource_id)
            if obj:
                for key, value in data.model_dump().items():
                    if hasattr(obj, key):
                        setattr(obj, key, value)
                session.add(obj)
                session.commit()
                session.refresh(obj)
            else:
                raise HTTPException(status_code=HTTPStatus.NOT_FOUND)
            return obj

    if "delete" in methods:

        @router.delete("/{resource_id}")
        def delete(
            resource_id: UUID,
            user_id: LoggedUserId,
            session: SessionDep,
            data: delete_dto = None,
        ):
            if delete_auth:
                user = session.get(User, user_id)
                if not delete_auth(data, user, resource_id):
                    raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED)
            obj = session.get(model, resource_id)
            if obj:
                session.delete(obj)
                session.commit()
            else:
                raise HTTPException(status_code=HTTPStatus.NOT_FOUND)

    return router
