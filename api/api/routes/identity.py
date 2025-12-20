from uuid import UUID

from api.dto import CreateUserIdentityIn
from api.models import User, UserIdentity
from api.crud import crud_router


async def create_auth(
    data: CreateUserIdentityIn, logged_user: User, _identity_id: None
):
    identity = await logged_user.awaitable_attrs.identity
    return data.user_id == logged_user.id and not identity


async def change_auth(
    data: CreateUserIdentityIn, logged_user: User, _identity_id: None
):
    identity = await logged_user.awaitable_attrs.identity
    return identity and identity.id == _identity_id and data.user_id == logged_user.id


async def get_auth(_: None, logged_user: User, identity_id: UUID):
    identity = await logged_user.awaitable_attrs.identity
    return identity and identity.id == identity_id


router = crud_router(
    UserIdentity,
    {"default": CreateUserIdentityIn},
    name="user-identity",
    methods=["get", "create", "put"],
    authorizations={"create": create_auth, "update": change_auth, "get": get_auth},
)
