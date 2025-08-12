from uuid import UUID
from datetime import date

from pydantic import BaseModel

from api.models import TermStatus


class CreateCourseIn(BaseModel):
    name: str
    description: str


class CreateCourseTermIn(BaseModel):
    status: TermStatus
    start_date: date
    end_date: date
    course_id: UUID
