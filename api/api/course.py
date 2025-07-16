from api.dto import CreateCourseIn
from api.models import Course, User, UserRole
from api.crud import crud_router


def auth(_: CreateCourseIn, user: User):
    return user.is_admin or user.role in [UserRole.INSTRUCTOR, UserRole.ADMIN]


router = crud_router(
    Course, {"default": CreateCourseIn}, authorizations={"default": auth}
)
