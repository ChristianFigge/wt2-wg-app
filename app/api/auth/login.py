from datetime import timedelta, datetime, timezone
from typing import Annotated

import jwt
from fastapi import Request, Depends, HTTPException, status
from jwt import InvalidTokenError
from sqlmodel import Session

from app.api.auth.utils import Hasher
from app.api.auth.utils import OAuth2PasswordBearerWithCookie
from app.db.crud.users import get_user_by_username
from app.db.models.user import User
from app.db.session import get_db
from app.schemas.tokens import TokenData
from app.settings import settings


def create_access_token_for_user(user: User):
    expires = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode = {
        "user": user.username,
        "exp": expires,
    }

    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt


def authenticate_user(username: str, password: str, db: Session) -> User | bool:
    user = get_user_by_username(username, db)
    if not user:
        return False
    if not Hasher.verify_password(password, user.hashed_password):
        return False
    return user


oauth2_scheme = OAuth2PasswordBearerWithCookie(tokenUrl="/login/token")


def get_user_by_token(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Annotated[Session, Depends(get_db)],  #Session = Depends(get_db)
):
    credentials_exception = HTTPException(
        status.HTTP_401_UNAUTHORIZED,
        "Invalid JWT Token ",
        {"WWW-Authenticate": "Bearer"},
    )

    # decode token & get username
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        print(f"JWT Payload: {payload}")
        username = payload.get("user")
        if username is None:
            credentials_exception.detail += "(Missing key 'user' in token payload dictionary)"
            raise credentials_exception
        token_data = TokenData(username=username)
    except InvalidTokenError:
        credentials_exception.detail += "(jwt.decode() failed)"
        raise credentials_exception

    # get user from db
    user = get_user_by_username(token_data.username, db)
    if user is None:
        credentials_exception.detail += f"(Username {token_data.username} doesn't exist in DB)"
        raise credentials_exception

    return user


async def is_logged_in(
        req: Request,
        db: Annotated[Session, Depends(get_db)]
):
    access_token = req.cookies.get("access_token")
    print(f">>> ACCESS TOKEN: {access_token}")

    if access_token and len(access_token) > 7:  # len("Bearer ") == 7
        try:
            current_user = get_user_by_token(access_token[7:], db)
            print(f">>> CURRENT USER: {current_user}")
            return current_user
        except HTTPException as http_ex:
            print(">>> Failed to recognize user by access token: " + http_ex.detail)

    return False
