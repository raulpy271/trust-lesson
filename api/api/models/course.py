import enum
from typing import List, Optional
from uuid import UUID, uuid4
from datetime import date

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from api.models.base import Base, TimestempMixin


class TermStatus(enum.Enum):
    WAITING = "WAITING"
    RUNNING = "RUNNING"
    FINISHED = "FINISHED"


class Course(TimestempMixin, Base):
    __tablename__ = "course"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    name: Mapped[str] = mapped_column(String(100))
    description: Mapped[Optional[str]] = mapped_column(String(255))
    terms_count: Mapped[int] = mapped_column(default=0, server_default="0")
    terms: Mapped[List["CourseTerm"]] = relationship(back_populates="course")


class CourseTerm(TimestempMixin, Base):
    __tablename__ = "course_term"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    term_number: Mapped[int] = mapped_column()
    status: Mapped[TermStatus] = mapped_column()
    start_date: Mapped[date] = mapped_column()
    end_date: Mapped[date] = mapped_column()
    course_id: Mapped[UUID] = mapped_column(
        ForeignKey("course.id", ondelete="no action")
    )
    course: Mapped["Course"] = relationship(back_populates="terms")
    users: Mapped[List["User"]] = relationship(
        secondary="term_user", back_populates="terms"
    )
    lessons: Mapped[List["Lesson"]] = relationship(back_populates="term")
