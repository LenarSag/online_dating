from pathlib import Path
from uuid import UUID

from fastapi import HTTPException, status, UploadFile

from config import UPLOAD_DIR, MAX_FILE_SIZE


def check_file(file: UploadFile) -> UploadFile:
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
    return file


def get_file_path(filename: str, unique_name: UUID) -> str:
    file_extension = Path(filename).suffix if Path(filename).suffix else '.bin'
    return str(Path(UPLOAD_DIR) / f'{unique_name}{file_extension}')
