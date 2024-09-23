import asyncio
import os

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import ValidationError
import uvicorn

from app.db.database import init_models
from app.endpoints.clients import clientrouter
from app.endpoints.login import loginrouter
from config import API_URL, UPLOAD_DIR


app = FastAPI()


app.include_router(clientrouter, prefix=f'{API_URL}/clients')
app.include_router(loginrouter, prefix=f'{API_URL}/auth')


@app.exception_handler(ValidationError)
async def custom_pydantic_validation_error_handler(
    request: Request, exc: ValidationError
):
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={'detail': exc.errors()},
    )


@app.exception_handler(RequestValidationError)
async def custom_fastapi_request_validation_error_handler(
    request: Request, exc: RequestValidationError
):
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={'detail': exc.errors()},
    )


def create_uploads_directory() -> None:
    if not os.path.exists(UPLOAD_DIR):
        os.mkdir(UPLOAD_DIR)


if __name__ == '__main__':
    create_uploads_directory()
    asyncio.run(init_models())
    uvicorn.run(app='main:app', host='127.0.0.1', port=8000, reload=True)
