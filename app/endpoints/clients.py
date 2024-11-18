from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi_filter import FilterDepends
from fastapi_pagination import Page, Params
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.user_repository import (
    create_match,
    create_mutual_match,
    get_match,
    get_paginated_users,
    get_reversed_match,
    get_user_by_id,
    update_user_coordinates,
)
from app.db.database import get_session
from app.models.user_model import User
from app.filters.user_filter import UserFilter
from app.schemas.location_schema import LocationBase
from app.schemas.user_schema import UserOut, UserWithCoordinates
from app.security.authentication import get_current_user
from app.utils.age import calculate_age
from app.utils.send_email import send_notification_about_match


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
    result = await get_paginated_users(session, user_filter, params, current_user)

    result.items = [
        UserOut(
            id=item.id,
            first_name=item.first_name,
            last_name=item.last_name,
            sex=item.sex,
            photo=item.photo,
            age=calculate_age(item.birth_date),
            distance_to=item.distance_to,
            tags=item.tags,
        )
        for item in result.items
    ]
    return result


@clientrouter.post('/{matching_user_id}/match')
async def match_user(
    matching_user_id: UUID,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    if current_user.id == matching_user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You can't match yourself",
        )

    matching_user = await get_user_by_id(session, matching_user_id)
    if not matching_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='User not found',
        )

    match = await get_match(session, current_user, matching_user_id)
    if match:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='You already matched this user',
        )
    new_match = await create_match(session, current_user, matching_user_id)

    reversed_match = await get_reversed_match(session, current_user, matching_user_id)
    if reversed_match:
        await create_mutual_match(session, new_match, reversed_match)
        # send notification emails to both users
        send_notification_about_match(current_user.email, matching_user)
        send_notification_about_match(matching_user.email, current_user)

        return JSONResponse(
            status_code=status.HTTP_201_CREATED,
            content={
                'status': 'mutual_match',
                'message': 'You and the user have both matched each other.',
                'matching_user_id': str(matching_user_id),
            },
        )

    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content={
            'status': 'match_pending',
            'message': 'You have matched the user. Waiting for them to match back.',
            'matching_user_id': str(matching_user_id),
        },
    )
