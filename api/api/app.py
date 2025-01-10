
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI

from api import public
from api import auth


def create_app():
    app = FastAPI()
    app.include_router(public.router)
    app.include_router(auth.router)
    app.add_middleware(auth.CheckAuthMiddleware)
    return app

app = create_app()

