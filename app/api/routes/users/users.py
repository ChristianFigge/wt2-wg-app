from typing import Annotated

from fastapi import APIRouter, Request, responses, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.exc import SQLAlchemyError
from sqlmodel import Session
from starlette import status
from starlette.responses import HTMLResponse, Response
from starlette.templating import Jinja2Templates

from app.api.auth.login import create_access_token_for_user, authenticate_user
from app.api.auth.login import is_logged_in
from app.api.routes.users.forms import LoginForm
from app.api.routes.users.forms import UserCreateForm
from app.db.crud.users import create_new_user
from app.db.crud.utils import value_exists
from app.db.models.user import User
from app.db.session import DbSession
from app.db.session import get_db
from app.schemas.tokens import Token
from app.schemas.users import UserCreate

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
            login_form.errors.append("Falscher Username oder Password!")

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
    return templates.TemplateResponse(req, "users/register.html", context={})


@router.post("/register")
async def register_new_user(req: Request, db: DbSession):
    form = UserCreateForm(req)
    form_is_valid = await form.load_data()
    if form_is_valid:

        if value_exists(User, User.username, form.username, db):
            form.errors.append("Dieser Nutzername ist bereits vergeben!")
            form.username = ""
        if value_exists(User, User.email, form.email, db):
            form.errors.append("Diese E-Mail Adresse ist bereits vergeben!")
            form.email = ""

        if not form.errors:
            user = UserCreate(
                username=form.username,
                plain_password=form.password,
                email=form.email
            )
            try:
                create_new_user(user, db)
                form.__dict__.update(signup_success=True)
                return templates.TemplateResponse("index.html", form.__dict__)
            except SQLAlchemyError as sqlEx:
                print(sqlEx)
                form.errors.append("Ein Datenbankfehler ist aufgetreten :(")

    return templates.TemplateResponse("users/register.html", form.__dict__)


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