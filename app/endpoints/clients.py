from fastapi import APIRouter, Depends
from fastapi_filter import FilterDepends
from fastapi_pagination import Page, Params
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.user_repository import (
    get_paginated_users,
    get_user_coordinates,
    update_user_coordinates,
)
from app.db.database import get_session
from app.models.user_model import User
from app.schemas.fastapi_models import UserFilter
from app.schemas.user_schema import LocationBase, UserOut, UserWithCoordinates
from app.security.authentication import get_current_user
from app.utils.age import calculate_age
from app.utils.coordinates import get_distance_between_coordinates


clientrouter = APIRouter()


@clientrouter.post('/update_coordinates', response_model=UserWithCoordinates)
async def update_coordinates(
    location: LocationBase,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    user = await update_user_coordinates(session, current_user, location)
    return user


@clientrouter.get('/', response_model=Page[UserOut])
async def get_clients_list(
    user_filter: UserFilter = FilterDepends(UserFilter),
    params: Params = Depends(),
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    current_user_coordinates = await get_user_coordinates(session, current_user)
    result = await get_paginated_users(session, user_filter, params, current_user)

    result.items = [
        UserOut(
            first_name=item.first_name,
            last_name=item.last_name,
            sex=item.sex,
            photo=item.photo,
            age=calculate_age(item.birth_date),
            distance_to=get_distance_between_coordinates(
                item.location, current_user_coordinates
            ),
            tags=item.tags,
        )
        for item in result.items
    ]
    return result
