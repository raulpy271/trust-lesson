import enum
from datetime import date
from typing import TYPE_CHECKING, Optional
from uuid import UUID, uuid4

from sqlmodel import Field, Relationship

from api.models.base import Base, TimestempMixin

if TYPE_CHECKING:
    from api.models.term_user import TermUser
    from api.models.lesson_user import LessonUser
    from api.models.lesson import Lesson, LessonValidation
    from api.models.validation import IdentityValidation


class UserRole(str, enum.Enum):
    STUDANT = "STUDANT"
    INSTRUCTOR = "INSTRUCTOR"
    ADMIN = "ADMIN"


class IdentityType(str, enum.Enum):
    IDENTITY_CARD = "IDENTITY_CARD"
    DRIVER_LICENSE = "DRIVER_LICENSE"
    PASSPORT = "PASSPORT"
    OTHER = "OTHER"


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
    identity: Optional["UserIdentity"] = Relationship(back_populates="user")
    identity_validation: Optional["IdentityValidation"] = Relationship(
        back_populates="user"
    )


class UserIdentity(TimestempMixin, Base, table=True):
    __tablename__ = "user_identity"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="user.id", unique=True)
    identity_code: str = Field(unique=True)
    type: IdentityType
    fullname: str
    parent_fullname: Optional[str]
    birth_date: date
    expiration_date: date
    issued_date: Optional[date]
    issuing_authority: Optional[str]
    country_state: Optional[str]
    user: "User" = Relationship(back_populates="identity")
