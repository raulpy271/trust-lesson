from uuid import UUID
from typing import Annotated, Optional
from datetime import datetime

from api.models.user import User
from pydantic import BaseModel, AfterValidator
from fastapi import UploadFile

from api.models import LessonStatus
from api.utils import check_media_type


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


class UploadSpreadsheetLessons(BaseModel):
    file: Annotated[
        UploadFile,
        AfterValidator(check_media_type(["xlsx"])),
    ]


class LessonInstructorOut(BaseModel):
    main: User.response_model()
    instructors: list[User.response_model()]
