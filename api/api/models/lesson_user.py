from uuid import UUID, uuid4

from sqlmodel import Field, Relationship

from api.models.base import Base


class LessonUser(Base, table=True):
    __tablename__ = "lesson_user"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    lesson_id: UUID = Field(foreign_key="lesson.id")
    user_id: UUID = Field(foreign_key="user.id")
    validated: bool = Field(default=False)
    validated_success: bool = Field(default=False)
    validations: list["LessonValidation"] = Relationship(back_populates="lesson_user")
    user: "User" = Relationship(back_populates="lesson_users")
    lesson: "Lesson" = Relationship(back_populates="lesson_users")
