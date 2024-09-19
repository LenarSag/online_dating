from datetime import datetime, timedelta
from typing import Optional
import uuid

import jwt
from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, HTTPException, status
from pydantic import EmailStr
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user_model import User
from app.crud.user_repository import get_user_by_id, get_user_by_email
from app.db.database import get_session
from app.security.pwd_crypt import verify_password
from config import ACCESS_TOKEN_EXPIRE_MINUTES, ALGORITHM, API_URL, SECRET_KEY


oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f'{API_URL}/auth/token/login')


async def authenticate_user(
    session: AsyncSession, email: EmailStr, password: str
) -> Optional[User]:
    user = await get_user_by_email(session, email)
    if not user or not verify_password(password, user.password):
        return None
    return user


def create_access_token(user: User) -> str:
    to_encode = {'sub': user.id}
    expire = datetime.now() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({'exp': expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def get_user_from_token(token: str = Depends(oauth2_scheme)) -> Optional[uuid.UUID]:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload.get('sub')

    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Token has expired',
            headers={'WWW-Authenticate': 'Bearer'},
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Invalid token',
            headers={'WWW-Authenticate': 'Bearer'},
        )


async def get_current_user(
    session: AsyncSession = Depends(get_session), id: int = Depends(get_user_from_token)
) -> Optional[User]:
    user = await get_user_by_id(session, id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Unauthorized, could not validate credentials.',
            headers={'WWW-Authenticate': 'Bearer'},
        )
    return user
