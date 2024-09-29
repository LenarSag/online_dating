import io
from pathlib import Path
import uuid

import aiofiles
from fastapi import HTTPException, status, UploadFile

from app.utils.watermark import add_watermark_to_photo
from config import FILE_CHUNK_SIZE, UPLOAD_DIR, MAX_FILE_SIZE


class FileSaver:
    def __init__(self, use_memory: bool = False):
        self.use_memory = use_memory
        self.in_memory_file = None

    def check_file(self, file: UploadFile) -> UploadFile:
        """Validate the file's type and size."""
        if file.content_type not in ("image/jpeg", "image/png"):
            raise HTTPException(
                detail="You can upload only images",
                status_code=status.HTTP_400_BAD_REQUEST,
            )
        if file.size > MAX_FILE_SIZE:
            raise HTTPException(
                detail="File is too big",
                status_code=status.HTTP_400_BAD_REQUEST,
            )
        return file

    def get_file_path(self, filename: str, unique_file_name: uuid.UUID) -> str:
        """Generate a unique file path for saving the file using a UUID."""
        unique_name = unique_file_name
        file_extension = Path(filename).suffix or ".bin"
        return str(Path(UPLOAD_DIR) / f"{unique_name}{file_extension}")

    async def save_file(self, in_file: UploadFile, unique_file_name: uuid.UUID):
        """Save the file either in memory or on disk after checking."""
        # Check if the file is valid
        self.check_file(in_file)
        # Generate the file path
        file_path = self.get_file_path(in_file.filename, unique_file_name)

        try:
            if self.use_memory:
                # Handle in-memory saving for tests
                self.in_memory_file = io.BytesIO(await in_file.read())
            else:
                # Handle actual disk saving
                async with aiofiles.open(file_path, "wb") as file:
                    while contents := await in_file.read(FILE_CHUNK_SIZE):
                        await file.write(contents)
        except Exception as e:
            raise HTTPException(
                detail={"message": f"Error during file uploading: {str(e)}"},
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
        finally:
            await in_file.close()

        return file_path

    async def add_watermark(self, file_path: str):
        """Add a watermark to the image."""
        if self.use_memory:
            # Use in-memory watermarking
            watermarked_bytes = add_watermark_to_photo(self.in_memory_file.getvalue())
            self.in_memory_file = io.BytesIO(watermarked_bytes)
        else:
            # Handle file-based watermarking
            async with aiofiles.open(file_path, "rb") as file:
                file_data = await file.read()

            watermarked_data = add_watermark_to_photo(file_data)

            async with aiofiles.open(file_path, "wb") as file:
                await file.write(watermarked_data)


def get_file_saver():
    return FileSaver(use_memory=False)
