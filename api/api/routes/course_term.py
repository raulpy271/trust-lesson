from uuid import UUID

from api.dto import CreateCourseTermIn
from api.models import CourseTerm, User, UserRole
from api.crud import crud_router


def auth(_: None | CreateCourseTermIn, user: User, _resource_id: None | UUID):
    return user.is_admin or user.role in [UserRole.INSTRUCTOR, UserRole.ADMIN]


router = crud_router(
    CourseTerm,
    {"default": CreateCourseTermIn, "delete": dict},
    name="course-term",
    authorizations={"default": auth, "list": None, "get": None},
)
