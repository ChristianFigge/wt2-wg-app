from sqlmodel import Session

from app.db.crud.users import create_new_user
from app.db.session import engine
from app.schemas.users import UserCreate

# Seed data
test_users = [
    {"username": "asd", "email": "asd@lol", "password": "asd"},
    {"username": "manfred", "email": "mananananan@lol.de", "password": "pass123"}
]

def seed_db():
    for user in test_users:
        new_user = UserCreate(
            username=user.get("username"),
            email=user.get("email"),
            plain_password=user.get("password")
        )
        create_new_user(new_user, Session(engine))

    print(">>> DB seeded successfully!")