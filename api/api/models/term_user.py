from typing import TYPE_CHECKING
from uuid import UUID

from sqlmodel import Field, Relationship

from api.models.base import Base
from api.models.user import UserRole

if TYPE_CHECKING:
    from api.models.course import CourseTerm
    from api.models.user import User


class TermUser(Base, table=True):
    __tablename__ = "term_user"

    term_id: UUID = Field(primary_key=True, foreign_key="course_term.id")
    user_id: UUID = Field(primary_key=True, foreign_key="user.id")
    term: "CourseTerm" = Relationship(back_populates="term_users")
    user: "User" = Relationship(back_populates="term_users")
    role: UserRole
