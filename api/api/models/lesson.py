import enum
from typing import Optional
from uuid import UUID, uuid4
from datetime import datetime

from sqlmodel import Field, Relationship

from api.models.base import Base, TimestempMixin
from api.models.lesson_user import LessonUser


class MediaType(enum.Enum):
    IMAGE = "IMAGE"
    VIDEO = "VIDEO"


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


class LessonValidation(TimestempMixin, Base, table=True):
    __tablename__ = "lesson_validation"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    lesson_id: UUID = Field(foreign_key="lesson.id")
    user_id: UUID = Field(foreign_key="user.id")
    validated: bool = Field(default=False)
    validated_success: bool = Field(default=False)
    validated_value: Optional[float]
    media_path: str
    media_type: MediaType
    lesson_user_id: UUID = Field(foreign_key="lesson_user.id")
    lesson: Lesson = Relationship(back_populates="validations")
    user: "User" = Relationship(back_populates="validations")
    lesson_user: LessonUser = Relationship(back_populates="validations")
