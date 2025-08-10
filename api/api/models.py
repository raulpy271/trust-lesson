import enum
from typing import List
from typing import Optional
from uuid import UUID, uuid4
from datetime import date, datetime

from sqlalchemy import ForeignKey, String, create_engine
from sqlalchemy.inspection import inspect
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
    relationship,
    sessionmaker,
)

from api import settings


class Base(DeclarativeBase):
    __exclude__ = ()

    def to_dict(self):
        instance = inspect(self)
        mapper = instance.mapper
        cols = mapper.column_attrs
        d = {c.key: getattr(self, c.key) for c in cols if c not in self.__exclude__}
        for key in mapper.relationships.keys():
            if key not in instance.unloaded:
                relation = getattr(self, key)
                if isinstance(relation, list):
                    d[key] = [r.to_dict() for r in relation]
                elif isinstance(relation, DeclarativeBase):
                    d[key] = relation.to_dict()
        return d


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

    def can_start(self):
        return self in (self.WAITING, self.LATE)

    def can_stop(self):
        return self in (self.RUNNING, self.LATE)


class MediaType(enum.Enum):
    IMAGE = "IMAGE"
    VIDEO = "VIDEO"


class TimestempMixin:
    created_at: Mapped[datetime] = mapped_column(default=datetime.now)
    updated_at: Mapped[datetime] = mapped_column(
        default=datetime.now, onupdate=datetime.now
    )


class TermUser(Base):
    __tablename__ = "term_user"

    term_id: Mapped[UUID] = mapped_column(
        ForeignKey("course_term.id", ondelete="no action"), primary_key=True
    )
    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("user.id", ondelete="no action"), primary_key=True
    )
    role: Mapped[UserRole] = mapped_column()


class LessonUser(Base):
    __tablename__ = "lesson_user"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    lesson_id: Mapped[UUID] = mapped_column(
        ForeignKey("lesson.id", ondelete="no action")
    )
    user_id: Mapped[UUID] = mapped_column(ForeignKey("user.id", ondelete="no action"))
    validated: Mapped[bool] = mapped_column(default=False, server_default="FALSE")
    validated_success: Mapped[bool] = mapped_column(
        default=False, server_default="FALSE"
    )
    validations: Mapped[List["LessonValidation"]] = relationship(
        back_populates="lesson_user"
    )


class User(TimestempMixin, Base):
    __tablename__ = "user"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    username: Mapped[str] = mapped_column(String(50))
    fullname: Mapped[str] = mapped_column(String(100))
    email: Mapped[str] = mapped_column(String(100), unique=True)
    role: Mapped[UserRole] = mapped_column(
        default=UserRole.STUDANT, server_default=UserRole.STUDANT.value
    )
    is_admin: Mapped[bool] = mapped_column(default=False, server_default="FALSE")
    password_hash: Mapped[str] = mapped_column(String(255))
    password_salt: Mapped[str] = mapped_column(String(255))
    terms: Mapped[List["CourseTerm"]] = relationship(
        secondary="term_user", back_populates="users"
    )
    ministrate_lessons: Mapped[List["Lesson"]] = relationship(
        back_populates="instructor"
    )
    lessons: Mapped[List["Lesson"]] = relationship(
        secondary="lesson_user", back_populates="users"
    )
    validations: Mapped[List["LessonValidation"]] = relationship(back_populates="user")


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


_engine = create_engine(settings.DB_URL)
_session = sessionmaker(_engine)


def Session():
    return _session()
