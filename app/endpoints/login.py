import json
import uuid
import aiofiles
from fastapi import APIRouter, Body, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.user_repository import create_user, get_user_by_email
from app.db.database import get_session
from app.schemas.user_schema import UserAuthentication, UserBase, UserCreate
from app.security.authentication import authenticate_user, create_access_token
from app.security.pwd_crypt import get_hashed_password
from app.utils.file import check_file, get_file_path
from app.utils.watermark import add_watermark_to_photo
from config import FILE_CHUNK_SIZE


loginrouter = APIRouter()


@loginrouter.post(
    '/users', response_model=UserBase, status_code=status.HTTP_201_CREATED
)
async def post_endpoint(
    user_data: UserCreate = Depends(),
    in_file: UploadFile = File(...),
    session: AsyncSession = Depends(get_session),
):
    user = await get_user_by_email(session, user_data.email)
    if user:
        raise HTTPException(
            detail='Email already taken', status_code=status.HTTP_400_BAD_REQUEST
        )

    user_id = uuid.uuid4()

    in_file = check_file(in_file)
    file_path = get_file_path(in_file.filename, user_id)

    try:
        # upload file by 1mb size chunks
        async with aiofiles.open(file_path, 'wb') as file:
            while contents := await in_file.read(FILE_CHUNK_SIZE):
                await file.write(contents)

        # open saved file to add watermark
        async with aiofiles.open(file_path, 'rb') as file:
            file_data = await file.read()

        # add watermark
        watermarked_data = add_watermark_to_photo(file_data)

        # save updated file
        async with aiofiles.open(file_path, 'wb') as file:
            await file.write(watermarked_data)

    except Exception as e:
        raise HTTPException(
            detail={'message': f'Error during file uploading: {str(e)}'},
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
    finally:
        await file.close()

    user_data.password = get_hashed_password(user_data.password)
    new_user = await create_user(session, user_data, user_id, file_path)
    return new_user


@loginrouter.post('/token/login', response_model=dict[str, str])
async def get_token(
    user_data: UserAuthentication, session: AsyncSession = Depends(get_session)
):
    user = await authenticate_user(session, user_data.email, user_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Invalid credentials',
            headers={'WWW-Authenticate': 'Bearer'},
        )
    access_token = create_access_token(user)
    return {'access_token': access_token, 'token_type': 'Bearer'}
