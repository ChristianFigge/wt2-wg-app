from typing import Any, Type

from sqlmodel import select, Session


def value_exists(table: Type, column: str, value: Any, db: Session) -> bool:
    stmt = select(table).where(column == value)
    res = db.exec(stmt).first()
    return res is not None