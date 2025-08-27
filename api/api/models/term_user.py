import enum
from uuid import UUID

from sqlmodel import Field, Relationship

from api.models.base import Base


class UserRole(str, enum.Enum):
    STUDANT = "STUDANT"
    INSTRUCTOR = "INSTRUCTOR"
    ADMIN = "ADMIN"


class TermUser(Base, table=True):
    __tablename__ = "term_user"

    term_id: UUID = Field(primary_key=True, foreign_key="course_term.id")
    user_id: UUID = Field(primary_key=True, foreign_key="user.id")
    term: "CourseTerm" = Relationship(back_populates="term_users")
    user: "User" = Relationship(back_populates="term_users")
    role: UserRole
