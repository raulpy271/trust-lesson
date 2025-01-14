
import enum
from typing import List
from typing import Optional
from uuid import UUID, uuid4
from datetime import date, datetime

from sqlalchemy import (
    ForeignKey,
    String,
    create_engine)
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
    relationship,
    sessionmaker)

from api import settings


class Base(DeclarativeBase):
    __exclude__ = ()
    
    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns if not c in self.__exclude__}

class UserRole(str, enum.Enum):
    STUDANT = "STUDANT"
    INSTRUCTOR = "INSTRUCTOR"
    ADMIN = "ADMIN"

class TermStatus(enum.Enum):
    WAITING = "WAITING"
    RUNNING = "RUNNING"
    FINISHED = "FINISHED"

class LessonStatus(enum.Enum):
    WAITING = "WAITING"
    RUNNING = "RUNNING"
    FINISHED = "FINISHED"
    LATE = "LATE"

class TimestempMixin:
    created_at: Mapped[datetime] = mapped_column(default=datetime.now)
    updated_at: Mapped[datetime] = mapped_column(default=datetime.now, onupdate=datetime.now)

class TermUser(Base):
    __tablename__ = "term_user"

    term_id: Mapped[UUID] = mapped_column(ForeignKey("course_term.id", ondelete="no action"), primary_key=True)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("user.id", ondelete="no action"), primary_key=True)
    role: Mapped[UserRole] = mapped_column()

class LessonUser(Base):
    __tablename__ = "lesson_user"

    lesson_id: Mapped[UUID] = mapped_column(ForeignKey("lesson.id", ondelete="no action"), primary_key=True)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("user.id", ondelete="no action"), primary_key=True)
    validated: Mapped[bool] = mapped_column(default=False, server_default="FALSE")

class User(TimestempMixin, Base):
    __tablename__ = "user"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    username: Mapped[str] = mapped_column(String(50))
    fullname: Mapped[str] = mapped_column(String(100))
    email: Mapped[str] = mapped_column(String(100), unique=True)
    role: Mapped[UserRole] = mapped_column(default=UserRole.STUDANT, server_default=UserRole.STUDANT.value)
    is_admin: Mapped[bool] = mapped_column(default=False, server_default="FALSE")
    password_hash: Mapped[str] = mapped_column(String(255))
    password_salt: Mapped[str] = mapped_column(String(255))
    terms: Mapped[List["CourseTerm"]] = relationship(secondary="term_user", back_populates="users")
    ministrate_lessons: Mapped[List["Lesson"]] = relationship(back_populates="instructor")
    lessons: Mapped[List["Lesson"]] = relationship(secondary="lesson_user", back_populates="users")

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
    course_id: Mapped[UUID] = mapped_column(ForeignKey("course.id", ondelete="no action"))
    course: Mapped["Course"] = relationship(back_populates="terms")
    users: Mapped[List["User"]] = relationship(secondary="term_user", back_populates="terms")
    lessons: Mapped[List["Lesson"]] = relationship(back_populates="term")

class Lesson(TimestempMixin, Base):
    __tablename__ = "lesson"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    status: Mapped[LessonStatus] = mapped_column(default=LessonStatus.WAITING, server_default=LessonStatus.WAITING.value)
    effective_start_date: Mapped[Optional[date]] = mapped_column()
    start_date: Mapped[date] = mapped_column()
    effective_duration_min: Mapped[Optional[int]] = mapped_column()
    duration_min: Mapped[int] = mapped_column()
    description: Mapped[Optional[str]] = mapped_column(String(255))
    instructor_id: Mapped[UUID] = mapped_column(ForeignKey("user.id", ondelete="no action"))
    term_id: Mapped[UUID] = mapped_column(ForeignKey("course_term.id", ondelete="no action"))
    instructor: Mapped["User"] = relationship(back_populates="ministrate_lessons")
    term: Mapped["CourseTerm"] = relationship(back_populates="lessons")
    users: Mapped[List["User"]] = relationship(secondary="lesson_user", back_populates="lessons")

_engine = create_engine(settings.DB_URL)
_session = sessionmaker(_engine)

def Session():
    return _session()

