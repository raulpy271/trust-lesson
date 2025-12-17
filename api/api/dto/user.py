from typing import Annotated
from http import HTTPStatus

from api.auth import validate_password
from pydantic import BaseModel, Field, AfterValidator
from fastapi import Query, HTTPException

from api.models import UserRole


PASSWORD_DESCRIPTION = "The password should contain both upper case and lower case characters. Besides it should contains numbers and symbols. The length of the password should be 10 up to 25."  # noqa: E501


def password_validation(password: str) -> str:
    if validate_password(password):
        return password
    else:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST, detail=PASSWORD_DESCRIPTION
        )


class CreateUserIn(BaseModel):
    username: str
    fullname: str
    email: str
    password: Annotated[str, AfterValidator(password_validation)] = Field(
        description=PASSWORD_DESCRIPTION
    )


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
