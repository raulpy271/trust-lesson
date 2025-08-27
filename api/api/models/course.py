import enum
from uuid import UUID, uuid4
from datetime import date

from sqlmodel import Field, Relationship

from api.models.base import Base, TimestempMixin
from api.models.term_user import TermUser


class TermStatus(enum.Enum):
    WAITING = "WAITING"
    RUNNING = "RUNNING"
    FINISHED = "FINISHED"


class Course(TimestempMixin, Base, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    name: str
    description: str
    terms_count: int = Field(default=0)
    terms: list["CourseTerm"] = Relationship(back_populates="course")


class CourseTerm(TimestempMixin, Base, table=True):
    __tablename__ = "course_term"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    term_number: int
    status: TermStatus
    start_date: date
    end_date: date
    course_id: UUID = Field(foreign_key="course.id")
    course: Course = Relationship(back_populates="terms")
    lessons: list["Lesson"] = Relationship(back_populates="term")
    term_users: list["TermUser"] = Relationship(back_populates="term")
