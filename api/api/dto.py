from uuid import UUID

from pydantic import BaseModel
from fastapi import UploadFile


class CreateCourseIn(BaseModel):
    name: str
    description: str


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
    database_healthy: bool | None = None
    database_error: str | None = None
    redis_healthy: bool | None = None
    redis_error: str | None = None
    storage_healthy: bool | None = None
    storage_error: str | None = None
