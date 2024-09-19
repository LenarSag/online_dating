import os
from uuid import UUID

from fastapi import HTTPException, status, UploadFile

from config import UPLOAD_DIR, MAX_FILE_SIZE


def check_file(file: UploadFile):
    if file.content_type not in (
        'image/jpeg',
        'image/png',
    ):
        raise HTTPException(
            detail='You can upload only images',
            status_code=status.HTTP_400_BAD_REQUEST,
        )
    if file.size > MAX_FILE_SIZE:
        raise HTTPException(
            detail='File is too big',
            status_code=status.HTTP_400_BAD_REQUEST,
        )


def get_file_path(filename: str, unique_name: UUID) -> str:
    file_extension = (
        os.path.splitext(filename)[1] if os.path.splitext(filename)[1] else '.bin'
    )
    return os.path.join(UPLOAD_DIR, f'{str(unique_name)}{file_extension}')
