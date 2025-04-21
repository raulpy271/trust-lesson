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


class HealthOut(BaseModel):
    database_healthy: bool = True
    database_error: str | None = None
    redis_healthy: bool = True
    redis_error: str | None = None
    storage_healthy: bool = True
    storage_error: str | None = None
