from typing import Annotated

from fastapi import Depends
from sqlmodel import SQLModel, create_engine, Session

# todo use settings for paths
sqlite_url = f"sqlite:///database.db"
engine = create_engine(sqlite_url, connect_args={"check_same_thread": False})


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def delete_db_and_tables():
    SQLModel.metadata.drop_all(engine)


def get_db():
    with Session(engine) as session:
        yield session

DbSession = Annotated[Session, Depends(get_db)]