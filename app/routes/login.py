import uuid
from fastapi import APIRouter, Depends, File, HTTPException, status, UploadFile

import aiofiles
from sqlalchemy.ext.asyncio import AsyncSession

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
    user = await check_username_and_email(session, user_data.username, user_data.email)
    if user:
        if user.username == user_data.username:
            raise HTTPException(
                detail='Имя уже используется.', status_code=status.HTTP_400_BAD_REQUEST
            )
        raise HTTPException(
            detail='Почта уже используется', status_code=status.HTTP_400_BAD_REQUEST
        )

    user_data.password = get_hashed_password(user_data.password)
    new_user = await create_user(session, user_data)

    return new_user
    check_file(in_file)
    unique_name = uuid.uuid4()
    file_path = get_file_path(in_file.filename, unique_name)

    async with aiofiles.open(file_path, 'wb') as out_file:
        content = await in_file.read()  # async read
        photo = add_watermark_to_photo(content)
        await out_file.write(photo)  # async write

    return {'Result': 'OK'}
