import enum
from typing import TYPE_CHECKING, Optional
from uuid import UUID, uuid4

from sqlmodel import Field, Relationship

from api.models.base import Base, TimestempMixin

if TYPE_CHECKING:
    from api.models.lesson import Lesson
    from api.models.lesson_user import LessonUser
    from api.models.user import User


class MediaType(enum.Enum):
    IMAGE = "IMAGE"
    VIDEO = "VIDEO"


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
    lesson: "Lesson" = Relationship(back_populates="validations")
    user: "User" = Relationship(back_populates="validations")
    lesson_user: "LessonUser" = Relationship(back_populates="validations")
