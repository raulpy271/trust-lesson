from uuid import UUID
from http import HTTPStatus

from fastapi import APIRouter, HTTPException

from api import dto
from api.crud import crud_router
from api.models import User, UserRole
from api.auth import create_hash_salt, check_hash
from api.depends import LoggedUserId, SessionDep


user_relationship = {
    "ministrate_lessons": {},
    "term_users": {"term"},
    "lesson_users": {"lesson"},
    "identity": {},
}


def is_admin_or_instructor(_data, logged_user: User, _resource_id):
    return logged_user.is_admin or logged_user.role == UserRole.INSTRUCTOR


def delete_auth(data: dto.DeleteUserIn, logged_user: User, user_id: UUID):
    password = data.password
    if password and check_hash(logged_user, password):
        return logged_user.is_admin or logged_user.id == user_id
    else:
        return False


def update_auth(data: dto.UpdateUserIn, logged_user: User, user_id: UUID):
    password = data.password
    if password and check_hash(logged_user, password):
        if logged_user.is_admin:
            return True
        elif logged_user.id == user_id:
            if not data.is_admin and data.role == logged_user.role:
                return True
    return False


router = APIRouter(prefix="/user", tags=["user"])


@router.post(
    "",
    status_code=HTTPStatus.CREATED,
    response_model=User.response_model(),
)
async def create(data: dto.CreateUserIn, session: SessionDep):
    data = data.model_dump()
    password = data.pop("password")
    phash, salt = create_hash_salt(password)
    data["password_hash"] = phash
    data["password_salt"] = salt
    user = User(**data)
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user


@router.get(
    "/me",
    response_model=User.response_model(user_relationship),
)
async def me(user_id: LoggedUserId, session: SessionDep):
    u = await session.get(User, user_id, options=User.selectload(user_relationship))
    if not u:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND)
    return u


crud_router(
    User,
    {"update": dto.UpdateUserIn, "delete": dto.DeleteUserIn},
    authorizations={
        "list": is_admin_or_instructor,
        "update": update_auth,
        "delete": delete_auth,
    },
    methods=["list", "put", "delete", "get"],
    router=router,
    response_model_relationship={
        "get": user_relationship,
        "update": user_relationship,
    },
)
