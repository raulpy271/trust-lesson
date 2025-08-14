from fastapi import FastAPI, APIRouter

from api.routes import routes, logged
from api.middleware import middlewares


def create_app():
    app = FastAPI()
    logged_router = APIRouter(
        prefix="/logged",
        tags=["logged"],
    )
    [logged_router.include_router(r) for r in logged]
    app.include_router(logged_router)
    [app.include_router(r) for r in routes]
    [app.add_middleware(m) for m in middlewares]
    return app


app = create_app()
