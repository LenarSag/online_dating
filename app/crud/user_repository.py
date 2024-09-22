from typing import Optional

from pydantic import EmailStr
from sqlalchemy.future import select
from sqlalchemy.sql.expression import or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user_model import User
from app.schemas.user_schema import UserCreate


async def get_user_by_email(session: AsyncSession, email: EmailStr) -> Optional[User]:
    query = select(User).filter_by(email=email)
    result = await session.execute(query)
    return result.scalar()


async def create_user(session: AsyncSession, user_data: UserCreate) -> User:
    user = User(**user_data.model_dump())
    session.add(user)
    await session.commit()
    return user
