from typing import Optional
import uuid

from fastapi_pagination import Params
from fastapi_pagination.ext.sqlalchemy import paginate
from pydantic import EmailStr
from sqlalchemy import and_, exists
from sqlalchemy.orm import selectinload
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user_model import Location, Match, User
from app.schemas.fastapi_models import UserFilter
from app.schemas.user_schema import LocationBase, UserCreate


async def get_user_by_email(session: AsyncSession, email: EmailStr) -> Optional[User]:
    query = select(User).filter_by(email=email)
    result = await session.execute(query)
    return result.scalar()


async def get_user_by_id(session: AsyncSession, id: uuid.UUID) -> Optional[User]:
    query = select(User).filter_by(id=id)
    result = await session.execute(query)
    return result.scalar()


async def create_user(
    session: AsyncSession, user_data: UserCreate, user_id: uuid.UUID, photo_path: str
) -> User:
    user = User(**user_data.model_dump())
    user.id = user_id
    user.photo = photo_path
    session.add(user)
    await session.flush()
    location = Location(user_id=user_id)
    session.add(location)
    await session.commit()
    return user


async def get_user_coordinates(
    session: AsyncSession, current_user: User
) -> Optional[Location]:
    query = select(Location).filter_by(user_id=current_user.id)
    result = await session.execute(query)
    return result.scalar()


async def update_user_coordinates(
    session: AsyncSession, user: User, location: LocationBase
) -> User:
    await session.refresh(user, attribute_names=('location',))
    user.location.latitude = location.latitude
    user.location.longitude = location.longitude
    await session.commit()
    return user


async def get_paginated_users(
    session: AsyncSession, user_filter: UserFilter, params: Params, current_user: User
):
    query = (
        select(User)
        .options(selectinload(User.tags))
        .options(selectinload(User.location))
        .filter(User.id != current_user.id)
    )
    query = user_filter.filter(query)
    query = user_filter.sort(query)
    return await paginate(
        session,
        query,
        params,
    )


async def match_exists(
    session: AsyncSession, current_user: User, matched_user_id: uuid.UUID
):
    query = select(
        exists().where(
            and_(
                Match.user_id == current_user.id,
                Match.matched_user_id == matched_user_id,
            )
        )
    )
    result = await session.execute(query)
    return result.scalar()


async def create_match(
    session: AsyncSession, current_user: User, matching_user_id: uuid.UUID
):
    match = Match(user_id=current_user.id, matched_user_id=matching_user_id)

    session.add(match)
    await session.flush()
    await session.commit()
    return match
