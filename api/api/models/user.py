from uuid import UUID, uuid4

from api.models.lesson import LessonValidation
from sqlmodel import Field, Relationship

from api.models.base import Base, TimestempMixin
from api.models.lesson_user import LessonUser
from api.models.term_user import UserRole, TermUser


class User(TimestempMixin, Base, table=True):
    __exclude__ = ("password_hash", "password_salt")

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    username: str
    fullname: str
    email: str = Field(unique=True)
    role: UserRole = Field(default=UserRole.STUDANT)
    is_admin: bool = Field(default=False)
    password_hash: str
    password_salt: str
    term_users: list["TermUser"] = Relationship(back_populates="user")
    ministrate_lessons: list["Lesson"] = Relationship(back_populates="instructor")
    lesson_users: list["LessonUser"] = Relationship(back_populates="user")
    validations: list["LessonValidation"] = Relationship(back_populates="user")
