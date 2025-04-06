from pydantic import BaseModel


class UserBase(BaseModel):
    username: str

class UserPublic(UserBase):
    id: int
    email: str | None = None

class UserProfile(UserBase):
    email: str

class UserCreate(UserProfile):
    plain_password: str
