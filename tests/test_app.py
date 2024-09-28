import math

from httpx import AsyncClient
import pytest
from sqlalchemy import event
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app import models
from app.db.database import get_session
from main import app
from config import API_URL


def acos(x):
    return math.acos(x)


def cos(x):
    return math.cos(x)


def sin(x):
    return math.sin(x)


def radians(x):
    return math.radians(x)


def register_math_functions(dbapi_conn, connection_record):
    dbapi_conn.create_function('acos', 1, acos)
    dbapi_conn.create_function('cos', 1, cos)
    dbapi_conn.create_function('sin', 1, sin)
    dbapi_conn.create_function('radians', 1, radians)
    print("Registered 'acos', 'cos', 'sin', and 'radians' functions.")


TEST_DATABASE_URL = 'sqlite+aiosqlite:///:memory:'


test_engine = create_async_engine(TEST_DATABASE_URL, echo=True)

event.listen(test_engine.sync_engine, 'connect', register_math_functions)

TestSessionLocal = sessionmaker(
    bind=test_engine, class_=AsyncSession, expire_on_commit=False
)


# Override the `get_session` to return an async session
async def override_get_session():
    session = TestSessionLocal()
    try:
        async with test_engine.begin() as conn:
            await conn.run_sync(models.Base.metadata.create_all)
        yield session
    finally:
        await session.close()


# Apply the override to FastAPI app
app.dependency_overrides[get_session] = override_get_session


@pytest.mark.asyncio
async def test_create_contact():
    query_params = {
        'email': 'newer@mail.com',
        'password': 'Q16werty!23',
        'first_name': 'newer',
        'last_name': 'newer',
        'sex': 'male',
        'birth_date': '2001-01-01',
    }

    file_path = 'app/media/photos/37c51031-bfd7-4f05-a457-976e43b1fb61.jpg'

    async with AsyncClient(
        app=app,
        base_url='http://test',
    ) as client:
        with open(file_path, 'rb') as file:
            files = {
                'in_file': (
                    file_path.split('/')[-1],
                    file,
                    'image/jpeg',
                ),
            }

            response = await client.post(
                f'{API_URL}/auth/clients/create', params=query_params, files=files
            )

            assert response.status_code == 201


@pytest.mark.asyncio
async def test_create_same_contact():
    query_params = {
        'email': 'newer@mail.com',
        'password': 'Q16werty!23',
        'first_name': 'newer',
        'last_name': 'newer',
        'sex': 'male',
        'birth_date': '2001-01-01',
    }

    file_path = 'app/media/photos/37c51031-bfd7-4f05-a457-976e43b1fb61.jpg'

    async with AsyncClient(
        app=app,
        base_url='http://test',
    ) as client:
        with open(file_path, 'rb') as file:
            files = {
                'in_file': (
                    file_path.split('/')[-1],
                    file,
                    'image/jpeg',
                ),
            }

            response = await client.post(
                f'{API_URL}/auth/clients/create', params=query_params, files=files
            )
            data = response.json()

            assert response.status_code == 400
            assert data['detail'] == 'Email already taken'


@pytest.mark.asyncio
async def test_get_token_and_protected_endpoint():
    login_payload = {
        'email': 'newer@mail.com',
        'password': 'Q16werty!23',
    }

    async with AsyncClient(
        app=app,
        base_url='http://test',
    ) as client:
        response = await client.post(
            f'{API_URL}/auth/token/login',
            json=login_payload,
        )
        login_data = response.json()

        assert response.status_code == 200
        assert 'access_token' in login_data

        access_token = login_data['access_token']
        headers = {
            'Authorization': f'Bearer {access_token}',
        }
        protected_response = await client.get(
            f'{API_URL}/clients/',
            headers=headers,
        )

        assert protected_response.status_code == 200
