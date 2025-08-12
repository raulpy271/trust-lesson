import enum
from typing import List, Optional
from uuid import UUID, uuid4
from datetime import datetime

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from api.models.base import Base, TimestempMixin
from api.models.user import User, LessonUser


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


class Lesson(TimestempMixin, Base):
    __tablename__ = "lesson"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    title: Mapped[str] = mapped_column(String(100))
    status: Mapped[LessonStatus] = mapped_column(
        default=LessonStatus.WAITING, server_default=LessonStatus.WAITING.value
    )
    effective_start_date: Mapped[Optional[datetime]] = mapped_column()
    start_date: Mapped[datetime] = mapped_column()
    effective_duration_min: Mapped[Optional[int]] = mapped_column()
    duration_min: Mapped[int] = mapped_column()
    description: Mapped[Optional[str]] = mapped_column(String(255))
    instructor_id: Mapped[UUID] = mapped_column(
        ForeignKey("user.id", ondelete="no action")
    )
    term_id: Mapped[UUID] = mapped_column(
        ForeignKey("course_term.id", ondelete="no action")
    )
    instructor: Mapped["User"] = relationship(back_populates="ministrate_lessons")
    term: Mapped["CourseTerm"] = relationship(back_populates="lessons")
    users: Mapped[List["User"]] = relationship(
        secondary="lesson_user", back_populates="lessons"
    )
    validations: Mapped[List["LessonValidation"]] = relationship(
        back_populates="lesson"
    )


class LessonValidation(TimestempMixin, Base):
    __tablename__ = "lesson_validation"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    lesson_id: Mapped[UUID] = mapped_column(
        ForeignKey("lesson.id", ondelete="no action")
    )
    user_id: Mapped[UUID] = mapped_column(ForeignKey("user.id", ondelete="no action"))
    validated: Mapped[bool] = mapped_column(default=False, server_default="FALSE")
    validated_success: Mapped[bool] = mapped_column(
        default=False, server_default="FALSE"
    )
    validated_value: Mapped[Optional[float]] = mapped_column()
    media_path: Mapped[str] = mapped_column()
    media_type: Mapped[MediaType] = mapped_column()
    lesson_user_id: Mapped[UUID] = mapped_column(
        ForeignKey("lesson_user.id", ondelete="no action")
    )
    lesson: Mapped[Lesson] = relationship(back_populates="validations")
    user: Mapped[User] = relationship(back_populates="validations")
    lesson_user: Mapped[LessonUser] = relationship(back_populates="validations")
