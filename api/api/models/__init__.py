from sqlmodel import create_engine
from sqlmodel import Session as _Session
from sqlalchemy.orm import sessionmaker

from api import settings
from api.models.course import (
    TermStatus,
    Course,
    CourseTerm,
)
from api.models.lesson import (
    MediaType,
    LessonStatus,
    Lesson,
    LessonValidation,
)
from api.models.user import (
    UserRole,
    TermUser,
    LessonUser,
    User,
)


_engine = create_engine(settings.DB_URL)


def Session():
    return _Session(_engine)
