from typing import Optional
import uuid

from fastapi_pagination import Page, Params
from fastapi_pagination.ext.sqlalchemy import paginate
from pydantic import EmailStr
from sqlalchemy.orm import selectinload
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user_model import Location, User
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
    session: AsyncSession, params: Params, current_user: User
):
    return await paginate(
        session,
        select(User)
        .options(selectinload(User.tags))
        .options(selectinload(User.location))
        .filter(User.id != current_user.id)
        .order_by(User.first_name),
        params,
    )
