from typing import Dict, cast, Any
from typing import Optional

from fastapi import HTTPException
from fastapi import Request
from fastapi import status
from fastapi.openapi.models import OAuthFlows as OAuthFlowsModel
from fastapi.security import OAuth2
from fastapi.security.utils import get_authorization_scheme_param
from passlib.context import CryptContext

from app.settings import settings


class OAuth2PasswordBearerWithCookie(OAuth2):
    def __init__(
            self,
            tokenUrl: str,
            scheme_name: Optional[str] = None,
            scopes: Optional[Dict[str, str]] = None,
            auto_error: bool = True,
    ):
        if not scopes:
            scopes = {}
        flows = OAuthFlowsModel(password=cast(Any, {"tokenUrl": tokenUrl, "scopes": scopes}))
        super().__init__(flows=flows, scheme_name=scheme_name, auto_error=auto_error)

    async def __call__(self, request: Request) -> Optional[str]:
        # original line in fastapi.OAuth2PasswordBearer class :
        #authorization = request.headers.get("Authorization")
        # ... changed to accept access token from httpOnly Cookie
        authorization: str = request.cookies.get("access_token")

        scheme, param = get_authorization_scheme_param(authorization)
        if not authorization or scheme.lower() != "bearer":
            if self.auto_error:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Not authenticated",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            else:
                return None
        return param


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class Hasher:
    @staticmethod
    def get_salted_password(plain_pw: str) -> str:
        return plain_pw + settings.PASSWORD_SALT

    @staticmethod
    def verify_password(plain_pw, hashed_pw):
        return pwd_context.verify(Hasher.get_salted_password(plain_pw), hashed_pw)

    @staticmethod
    def hash_password(plain_pw: str) -> str:
        return pwd_context.hash(Hasher.get_salted_password(plain_pw))
