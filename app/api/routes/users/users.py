from typing import Annotated

from fastapi.security import OAuth2PasswordRequestForm
from starlette import status

from app.api.auth.forms import LoginForm
from app.api.auth.login import create_access_token_for_user, authenticate_user
from app.api.auth.login import is_logged_in
from app.db.crud.users import create_new_user
from app.db.models.user import User
from app.db.session import DbSession
from app.db.session import get_db
from fastapi import APIRouter, Request, responses, Depends, HTTPException

from app.schemas.tokens import Token
from app.schemas.users import UserCreate
from sqlmodel import Session
from starlette.responses import HTMLResponse, Response
from starlette.templating import Jinja2Templates

templates = Jinja2Templates(directory="app/html_templates")
router = APIRouter()


@router.get("/login", response_class=HTMLResponse)
def get_login_form(req: Request):
    return templates.TemplateResponse(req, "auth/login.html", context={})


@router.post("/login")
async def login_user(req: Request, db: Session = Depends(get_db)):
    login_form = LoginForm(req)
    form_is_valid = await login_form.load_data()
    if form_is_valid:
        try:
            resp = responses.RedirectResponse("/home", status.HTTP_302_FOUND)  # status 302 forces GET method
            login_for_access_token(resp, login_form, db)
            return resp
        except HTTPException:
            login_form.__dict__.get("errors").append("Falscher Username oder Password!")
            return templates.TemplateResponse("auth/login.html", login_form.__dict__)  #

    return templates.TemplateResponse("auth/login.html", login_form.__dict__)


@router.post("/login/token", response_model=Token)
def login_for_access_token(
        resp: Response,
        form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
        db: Annotated[Session, Depends(get_db)],
):
    user = authenticate_user(form_data.username, form_data.password, db)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )

    access_token = create_access_token_for_user(user)
    print(f"Access Token created: {access_token}")
    resp.set_cookie(key="access_token", value=f"Bearer {access_token}", httponly=True)
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/register", response_class=HTMLResponse)
def register_form(req: Request):
    return templates.TemplateResponse(req, "register.html", context={})


@router.post("/register")
async def register_new_user(req: Request, db: DbSession) -> User:
    form = await req.form()
    user_form = UserCreate(username=form.get("username"), password=form.get("password"))
    new_user = create_new_user(user_form, db)
    return new_user


@router.get("/profile")
async def profile_page(
    req: Request,
    db: Session = Depends(get_db),
):
    user = await is_logged_in(req, db)
    context = {"request": req, "user": user}

    return templates.TemplateResponse("users/profile.html", context)


@router.get("/logout")
async def logout_user(req: Request):
    resp = responses.RedirectResponse("/")
    resp.delete_cookie(key="access_token")
    return resp