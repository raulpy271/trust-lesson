import enum
from typing import TYPE_CHECKING, Optional
from uuid import UUID, uuid4
from datetime import datetime

from sqlmodel import Field, Relationship

from api.models.base import Base, TimestempMixin

if TYPE_CHECKING:
    from api.models.lesson_user import LessonUser
    from api.models.user import User
    from api.models.course import CourseTerm
    from api.models.validation import LessonValidation


class LessonStatus(enum.Enum):
    WAITING = "WAITING"
    RUNNING = "RUNNING"
    FINISHED = "FINISHED"
    LATE = "LATE"

    def can_start(self):
        return self in (self.WAITING, self.LATE)

    def can_stop(self):
        return self in (self.RUNNING, self.LATE)


class Lesson(TimestempMixin, Base, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    title: str
    status: LessonStatus = Field(default=LessonStatus.WAITING)
    effective_start_date: Optional[datetime]
    start_date: datetime
    effective_duration_min: Optional[int]
    duration_min: int
    description: str
    instructor_id: UUID = Field(foreign_key="user.id")
    term_id: UUID = Field(foreign_key="course_term.id")
    instructor: "User" = Relationship(back_populates="ministrate_lessons")
    term: "CourseTerm" = Relationship(back_populates="lessons")
    lesson_users: list["LessonUser"] = Relationship(back_populates="lesson")
    validations: list["LessonValidation"] = Relationship(back_populates="lesson")
