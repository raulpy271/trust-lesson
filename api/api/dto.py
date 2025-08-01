from datetime import date, datetime
from typing import Annotated, Optional
from uuid import UUID

from pydantic import BaseModel, AfterValidator
from fastapi import UploadFile, Query

from api.models import LessonStatus, TermStatus, UserRole
from api.utils import check_media_type


class CreateCourseIn(BaseModel):
    name: str
    description: str


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


class CreateCourseTermIn(BaseModel):
    status: TermStatus
    start_date: date
    end_date: date
    course_id: UUID


class CreateLessonIn(BaseModel):
    title: str
    status: LessonStatus = LessonStatus.WAITING
    start_date: datetime
    duration_min: int
    description: Optional[str] = None
    instructor_id: UUID
    term_id: UUID


class UpdateLessonIn(BaseModel):
    title: str
    status: LessonStatus = LessonStatus.WAITING
    start_date: datetime
    duration_min: int
    description: Optional[str] = None
    effective_start_date: Optional[datetime]
    effective_duration_min: Optional[int]
    instructor_id: UUID


class LoginIn(BaseModel):
    email: str
    password: str


class ValidationIn(BaseModel):
    lesson_id: UUID
    file: Annotated[
        UploadFile,
        AfterValidator(
            check_media_type(["png", "jpeg", "jpg"], mime_types=["image", "video"])
        ),
    ]


class HealthOut(BaseModel):
    database_healthy: bool | None = None
    database_error: str | None = None
    redis_healthy: bool | None = None
    redis_error: str | None = None
    storage_healthy: bool | None = None
    storage_error: str | None = None


class UploadSpreadsheetLessons(BaseModel):
    file: Annotated[
        UploadFile,
        AfterValidator(check_media_type(["xlsx"])),
    ]
