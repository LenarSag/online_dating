from datetime import date
from typing import Optional
from fastapi_filter.contrib.sqlalchemy import Filter
from pydantic import BaseModel

from app.models.user_model import User, UserSex


class Token(BaseModel):
    access_token: str
    token_type: str


class UserFilter(Filter):
    first_name: Optional[str] = None
    first_name__ilike: Optional[str] = None
    last_name: Optional[str] = None
    last_name__ilike: Optional[str] = None
    sex: Optional[UserSex] = None
    birth_date__lt: Optional[date] = None
    birth_date__gt: Optional[date] = None
    order_by: list[str] = ['first_name']

    class Constants(Filter.Constants):
        model = User
