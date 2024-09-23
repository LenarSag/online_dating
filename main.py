import asyncio
import os

from fastapi import FastAPI
import uvicorn

from app.db.database import init_models
from app.endpoints.login import loginrouter
from config import API_URL, UPLOAD_DIR


app = FastAPI()


app.include_router(loginrouter, prefix=f'{API_URL}/auth')


def create_uploads_directory() -> None:
    if not os.path.exists(UPLOAD_DIR):
        os.mkdir(UPLOAD_DIR)


if __name__ == '__main__':
    create_uploads_directory()
    asyncio.run(init_models())
    uvicorn.run(app='main:app', host='127.0.0.1', port=8000, reload=True)
