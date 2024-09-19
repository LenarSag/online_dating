import os

from fastapi import FastAPI
import uvicorn

from app.routes.login import loginrouter
from config import UPLOAD_DIR


app = FastAPI()


app.include_router(loginrouter, prefix='/auth')


def create_uploads_directory():
    if not os.path.exists(UPLOAD_DIR):
        os.mkdir(UPLOAD_DIR)


if __name__ == '__main__':
    create_uploads_directory()
    uvicorn.run(app='main:app', host='127.0.0.1', port=8000, reload=True)
