from uuid import UUID
from http import HTTPStatus

from fastapi import APIRouter, HTTPException

from api import dto
from api.crud import crud_router
from api.models import Session, User
from api.auth import create_hash_salt, check_hash
from api.depends import LoggedUserId


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


@router.post("/", status_code=HTTPStatus.CREATED)
def create(data: dto.CreateUserIn):
    with Session() as session:
        data = data.model_dump()
        password = data.pop("password")
        phash, salt = create_hash_salt(password)
        data["password_hash"] = phash
        data["password_salt"] = salt
        user = User(**data)
        session.add(user)
        session.commit()
    return {}


@router.get("/me")
def me(user_id: LoggedUserId):
    with Session() as session:
        u = session.get(User, user_id)
        if not u:
            raise HTTPException(status_code=HTTPStatus.NOT_FOUND)
    return u.to_dict()


crud_router(
    User,
    {"update": dto.UpdateUserIn, "delete": dto.DeleteUserIn},
    authorizations={"update": update_auth, "delete": delete_auth},
    methods=["list", "put", "delete", "get"],
    router=router,
)
