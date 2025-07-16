from uuid import UUID

from api.dto import CreateCourseIn
from api.models import Course, User, UserRole
from api.crud import crud_router


def auth(_: None | CreateCourseIn, user: User, _resource_id: None | UUID):
    return user.is_admin or user.role in [UserRole.INSTRUCTOR, UserRole.ADMIN]


router = crud_router(
    Course,
    {"default": CreateCourseIn, "delete": dict},
    authorizations={"default": auth, "list": None},
)
