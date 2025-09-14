from sqlmodel.ext.asyncio.session import AsyncSession as _AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine


from api import settings
from api.models.term_user import TermUser
from api.models.lesson_user import LessonUser
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
    User,
)


_async_engine = create_async_engine(settings.DB_URL)


def AsyncSession():
    return _AsyncSession(_async_engine, expire_on_commit=False)
