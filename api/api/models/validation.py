import enum
from datetime import date
from typing import TYPE_CHECKING, Optional
from uuid import UUID, uuid4

from sqlmodel import Field, Relationship

from api.models.base import Base, TimestempMixin
from api.models.user import IdentityType

if TYPE_CHECKING:
    from api.models.lesson import Lesson
    from api.models.lesson_user import LessonUser
    from api.models.user import User


class MediaType(enum.Enum):
    IMAGE = "IMAGE"
    VIDEO = "VIDEO"


class LessonValidation(TimestempMixin, Base, table=True):
    __tablename__ = "lesson_validation"
    __exclude__ = ("error_traceback",)

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    lesson_id: UUID = Field(foreign_key="lesson.id")
    user_id: UUID = Field(foreign_key="user.id")
    validated: bool = Field(default=False)
    validated_success: bool = Field(default=False)
    error_message: Optional[str]
    error_traceback: Optional[str]
    confidence: Optional[float]
    media_path: str
    media_type: MediaType
    lesson_user_id: UUID = Field(foreign_key="lesson_user.id")
    lesson: "Lesson" = Relationship(back_populates="validations")
    user: "User" = Relationship(back_populates="validations")
    lesson_user: "LessonUser" = Relationship(back_populates="validations")


class IdentityValidation(TimestempMixin, Base, table=True):
    __tablename__ = "identity_validation"
    __exclude__ = ("error_traceback",)

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="user.id")
    validated: bool = Field(default=False)
    validated_success: bool = Field(default=False)
    error_message: Optional[str]
    error_traceback: Optional[str]
    image_path: str
    identity_code: Optional[str]
    identity_code_confidence: Optional[float]
    type: Optional[IdentityType]
    type_confidence: Optional[float]
    fullname: Optional[str]
    fullname_confidence: Optional[float]
    parent_fullname: Optional[str]
    parent_fullname_confidence: Optional[float]
    birth_date: Optional[date]
    birth_date_confidence: Optional[float]
    expiration_date: Optional[date]
    expiration_date_confidence: Optional[float]
    issued_date: Optional[date]
    issued_date_confidence: Optional[float]
    issuing_authority: Optional[str]
    issuing_authority_confidence: Optional[float]
    country_state: Optional[str]
    country_state_confidence: Optional[float]
    user: "User" = Relationship(back_populates="identity_validation")
