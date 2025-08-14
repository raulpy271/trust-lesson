import enum
from typing import List
from uuid import UUID, uuid4

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from api.models.base import Base, TimestempMixin


class UserRole(str, enum.Enum):
    STUDANT = "STUDANT"
    INSTRUCTOR = "INSTRUCTOR"
    ADMIN = "ADMIN"


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
