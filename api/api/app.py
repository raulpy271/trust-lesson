
from fastapi import FastAPI, APIRouter

from api import public
from api import user
from api import auth


def create_app():
    app = FastAPI()
    logged_router = APIRouter(
        prefix="/logged",
        tags=["logged"],
    )
    logged_router.include_router(user.router)
    app.include_router(public.router)
    app.include_router(auth.router)
    app.include_router(logged_router)
    app.add_middleware(auth.CheckAuthMiddleware)
    return app

app = create_app()

