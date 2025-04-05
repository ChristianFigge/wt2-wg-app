from sqlmodel import Session, select

from app.api.auth.utils import Hasher
from app.db.models.user import User
from app.schemas.users import UserCreate


def create_new_user(user: UserCreate, db: Session):
    new_db_user = User(
        username=user.username,
        hashed_password=Hasher.hash_password(user.password)
    )
    db.add(new_db_user)
    db.commit()
    db.refresh(new_db_user)
    return new_db_user

def get_user_by_username(uname: str, db: Session):
    stmt = select(User).where(User.username == uname)
    user = db.exec(stmt).first()
    return user