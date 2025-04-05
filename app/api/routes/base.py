from app.api.routes.users import users
from fastapi import APIRouter, Depends, responses
from sqlmodel import Session
from starlette.requests import Request
from starlette.responses import HTMLResponse
from starlette.templating import Jinja2Templates

from app.api.auth.login import is_logged_in
from app.db.session import get_db

api_router = APIRouter()

api_router.include_router(users.router, prefix="", tags=["users"])


templates = Jinja2Templates(directory="app/html_templates")


@api_router.get("/")
def root_page():
    return responses.RedirectResponse("/home") # redirect test


@api_router.get("/home", response_class=HTMLResponse)
async def home_page(
    req: Request,
    db: Session = Depends(get_db),
):
    # check if client is a logged in user and set context accordingly
    user = await is_logged_in(req, db)
    context = {"request": req, "user": user}

    # return html template with the context set above
    return templates.TemplateResponse("index.html", context)


@api_router.get("/test")
def test():
    return {"lol" : "hi"}