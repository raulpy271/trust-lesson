from uuid import UUID
from http import HTTPStatus

from sqlalchemy import select

from api import dto
from api.crud import crud_router
from api.models import Session, User
from api.auth import create_hash_salt, check_hash, LoggedUserId


def auth(data, logged_user: User, user_id: UUID):
    password = (
        data
        if isinstance(data, str)
        else data.password if hasattr(data, "password") else None
    )
    if password and check_hash(logged_user, password):
        return logged_user.is_admin or logged_user.id == user_id
    else:
        return False


router = crud_router(
    User,
    {"default": dto.CreateUserIn, "delete": dto.DeleteUserIn},
    authorizations={"put": auth, "delete": auth},
    methods=["list", "put", "delete"],
)


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
        u = session.scalars(select(User).where(User.id == user_id)).one()
    return u.to_dict()
