from fastapi import FastAPI, APIRouter

from api import public
from api import user
from api import auth
from api import lesson
from api import validation
from api import course
from api import course_term


def create_app():
    app = FastAPI()
    logged_router = APIRouter(
        prefix="/logged",
        tags=["logged"],
    )
    logged_router.include_router(user.router)
    logged_router.include_router(lesson.router)
    logged_router.include_router(validation.router)
    logged_router.include_router(course.router)
    logged_router.include_router(course_term.router)
    app.include_router(public.router)
    app.include_router(auth.router)
    app.include_router(logged_router)
    app.add_middleware(auth.CheckAuthMiddleware)
    return app


app = create_app()
