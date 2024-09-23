from typing import Optional
import uuid

from pydantic import EmailStr
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user_model import User
from app.schemas.user_schema import UserCreate


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
    await session.commit()
    return user
