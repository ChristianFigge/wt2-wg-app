from sqlmodel import Session

from app.db.crud.users import create_new_user
from app.db.session import engine
from app.schemas.users import UserCreate

# Seed data
test_users = [
    {"username": "asd", "password": "asd"},
    {"username": "manfred", "password": "pass123"}
]

def seed_db():
    for user in test_users:
        new_user = UserCreate(
            username=user.get("username"),
            password=user.get("password")
        )
        create_new_user(new_user, Session(engine))

    print(">>> DB seeded successfully!")