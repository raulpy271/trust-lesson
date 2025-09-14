from contextlib import asynccontextmanager

from fastapi import FastAPI, APIRouter

from api.routes import routes, logged
from api.middleware import middlewares
from api.redis import get_default_client
from api.azure.storage import close_resources


@asynccontextmanager
async def lifespan(app: FastAPI):
    client = get_default_client()
    yield
    await client.aclose()
    await close_resources()


def create_app():
    app = FastAPI(lifespan=lifespan)
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
