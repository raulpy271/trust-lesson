from uuid import UUID

from pydantic import BaseModel
from fastapi import UploadFile


class CreateUserIn(BaseModel):
    username: str
    fullname: str
    email: str
    password: str


class LoginIn(BaseModel):
    email: str
    password: str


class ValidationIn(BaseModel):
    lesson_id: UUID
    file: UploadFile
