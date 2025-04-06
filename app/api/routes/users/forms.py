import re
from typing import List
from typing import Optional

from fastapi import Request


class LoginForm:
    def __init__(self, request: Request):
        self.request: Request = request
        self.errors: List = []
        self.username: Optional[str] = None
        self.password: Optional[str] = None

    async def load_data(self) -> bool:
        form = await self.request.form()
        self.username = form.get("username")
        self.password = form.get("password")
        return self.is_valid()

    def is_valid(self) -> bool:
        if not self.username:
            self.errors.append("Username is required")
        if not self.password:  # or not len(self.password) >= 4:
            self.errors.append("A valid password is required")
        if not self.errors:
            return True
        return False


forbidden_email_chars = re.compile("[^a-z0-9@._-]")
email_specials = re.compile("[@._-]")


class UserCreateForm:
    def __init__(self, request: Request):
        self.request: Request = request
        self.errors: List = []
        self.username: Optional[str] = None
        self.email: Optional[str] = None
        self.password: Optional[str] = None

    async def load_data(self) -> bool:
        form = await self.request.form()
        self.username = form.get("username").strip()
        self.email = form.get("email").strip().lower()
        self.password = form.get("password")
        return self.is_valid()

    def is_valid(self) -> bool:
        if not self.username or len(self.username) < 3:
            self.username = ""
            self.errors.append("Usernamen müssen aus mindestens 3 Zeichen bestehen")
        if not self.email or not self.email_is_valid():
            self.email = ""
            self.errors.append("Bitte geben Sie eine gültige E-Mail Adresse an")
        if not self.password or len(self.password) < 3:
            self.errors.append("Passwörter müssen aus mindestens 3 Zeichen bestehen")
        if not self.errors:
            return True
        return False

    # https://snov.io/knowledgebase/what-is-a-valid-email-address-format/
    # bisschen overkill vielleicht
    def email_is_valid(self) -> bool:
        try:
            user, domain = self.email.split("@")
        except ValueError:
            return False

        domain_parts = domain.split(".")
        if len(domain_parts) < 2 or len(domain_parts[-1]) < 2:
            return False

        # Sonderzeichen checken: Mehrfache SZ und SZ am Anfang/Ende
        for substr in email_specials.split(self.email):
            if not substr: # empty
                return False

        if forbidden_email_chars.search(self.email):
            return False

        return True
