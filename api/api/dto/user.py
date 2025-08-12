from typing import Annotated

from pydantic import BaseModel
from fastapi import Query

from api.models import UserRole


class CreateUserIn(BaseModel):
    username: str
    fullname: str
    email: str
    password: str


class UpdateUserIn(BaseModel):
    username: str
    fullname: str
    email: str
    password: str
    role: UserRole
    is_admin: bool


class DeleteUserParams(BaseModel):
    password: str


DeleteUserIn = Annotated[DeleteUserParams, Query()]
