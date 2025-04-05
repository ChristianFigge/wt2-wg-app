from pydantic import BaseModel


class UserCreate(BaseModel):
    username: str
    password: str


class UserInDB(UserCreate):
    hashed_password: str
