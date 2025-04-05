from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.routes.base import api_router
from app.db.seeding import seed_db
from app.db.session import create_db_and_tables, delete_db_and_tables
from app.settings import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    # on startup:
    delete_db_and_tables()
    create_db_and_tables()
    seed_db()

    yield  # run the app

    # on shutdown:
    print("TSCHÜSS")


def start_app():
    fastapi_app = FastAPI(title=settings.PROJECT_NAME, version=settings.PROJECT_VERSION, lifespan=lifespan)
    fastapi_app.include_router(api_router)
    return fastapi_app


app = start_app()
