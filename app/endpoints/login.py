import uuid

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.user_repository import create_user, get_user_by_email
from app.db.database import get_session
from app.schemas.fastapi_models import Token
from app.schemas.user_schema import UserAuthentication, UserBase, UserCreate
from app.security.authentication import authenticate_user, create_access_token
from app.security.pwd_crypt import get_hashed_password
from app.utils.files_handling import FileSaver, get_file_saver
from app.utils.unique_id import get_new_user_id


loginrouter = APIRouter()


@loginrouter.post(
    "/clients/create", response_model=UserBase, status_code=status.HTTP_201_CREATED
)
async def post_endpoint(
    user_data: UserCreate = Depends(),
    in_file: UploadFile = File(...),
    session: AsyncSession = Depends(get_session),
    new_user_id: uuid.UUID = Depends(get_new_user_id),
    file_saver: FileSaver = Depends(get_file_saver),
):
    user = await get_user_by_email(session, user_data.email)
    if user:
        raise HTTPException(
            detail="Email already taken", status_code=status.HTTP_400_BAD_REQUEST
        )

    file_path = await file_saver.save_file(in_file, new_user_id)
    await file_saver.add_watermark(file_path)

    user_data.password = get_hashed_password(user_data.password)
    new_user = await create_user(session, user_data, new_user_id, file_path)
    return new_user


@loginrouter.post("/token/login", response_model=Token)
async def get_token(
    user_data: UserAuthentication, session: AsyncSession = Depends(get_session)
):
    user = await authenticate_user(session, user_data.email, user_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(user)
    return Token(access_token=access_token, token_type="Bearer")
