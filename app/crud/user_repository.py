from typing import Optional
import uuid

from fastapi_pagination import Params
from fastapi_pagination.ext.sqlalchemy import paginate
from pydantic import EmailStr
from sqlalchemy import and_, exists, func
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload, with_expression

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
    await session.refresh(current_user, attribute_names=('location',))

    current_latitude = current_user.location.latitude
    current_longitude = current_user.location.longitude

    # Subquery to get users liked by the current user
    liked_users_subquery = (
        select(Match.matched_user_id)
        .filter(Match.user_id == current_user.id)
        .subquery()
    )

    query = (
        select(User)
        .join(User.location)
        .options(selectinload(User.tags))
        .options(
            with_expression(
                User.distance_to,
                6371.0
                * func.acos(
                    func.cos(func.radians(current_latitude))
                    * func.cos(func.radians(Location.latitude))
                    * func.cos(
                        func.radians(Location.longitude)
                        - func.radians(current_longitude)
                    )
                    + func.sin(func.radians(current_latitude))
                    * func.sin(func.radians(Location.latitude))
                ),
            )
        )
        .filter(User.id != current_user.id)
        .filter(User.id.not_in(select(liked_users_subquery)))
    )

    print('leo', user_filter.distance_to__lt)
    # Apply filtering and sorting
    query = user_filter.filter(query)
    query = user_filter.sort(query)

    # Paginate and return the result
    return await paginate(session, query, params)


async def match_exists(
    session: AsyncSession, current_user: User, matched_user_id: uuid.UUID
) -> Optional[bool]:
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


async def create_mutual_match(
    session: AsyncSession, user_match: Match, target_user_match: Match
) -> None:
    user_match.is_mutual = True
    target_user_match.is_mutual = True
    await session.commit()


async def get_match(
    session: AsyncSession, current_user: User, matched_user_id: uuid.UUID
) -> Optional[Match]:
    query = select(Match).where(
        and_(
            Match.user_id == current_user.id,
            Match.matched_user_id == matched_user_id,
        )
    )
    result = await session.execute(query)
    return result.scalar()


async def get_reversed_match(
    session: AsyncSession, current_user: User, matched_user_id: uuid.UUID
) -> Optional[Match]:
    query = select(Match).where(
        and_(
            Match.user_id == matched_user_id,
            Match.matched_user_id == current_user.id,
        )
    )
    result = await session.execute(query)
    return result.scalar()


async def create_match(
    session: AsyncSession, current_user: User, matching_user_id: uuid.UUID
) -> Match:
    match = Match(user_id=current_user.id, matched_user_id=matching_user_id)
    session.add(match)
    await session.flush()
    await session.commit()
    return match
