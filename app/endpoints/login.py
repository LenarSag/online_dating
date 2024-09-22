import uuid

import aiofiles
from fastapi import APIRouter, Depends, File, HTTPException, status, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.user_repository import create_user, get_user_by_email
from app.db.database import get_session
from app.schemas.user_schema import UserCreate
from app.security.pwd_crypt import get_hashed_password
from app.utils.file import check_file, get_file_path
from app.utils.watermark import add_watermark_to_photo


loginrouter = APIRouter()


@loginrouter.post('/')
async def post_endpoint(
    user_data: UserCreate,
    in_file: UploadFile = File(...),
    session: AsyncSession = Depends(get_session),
):
    user = await get_user_by_email(session, user_data.email)
    if user:
        raise HTTPException(
            detail='Email already taken', status_code=status.HTTP_400_BAD_REQUEST
        )

    user_data.password = get_hashed_password(user_data.password)
    new_user = await create_user(session, user_data)

    return new_user
