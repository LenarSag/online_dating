import io
import math

from fastapi import status
from httpx import AsyncClient, ASGITransport
from PIL import Image
import pytest
from sqlalchemy import event
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app import models
from app.db.database import get_session
from app.utils.files_handling import FileSaver, get_file_saver
from main import app
from config import API_URL


TEST_DATABASE_URL = 'sqlite+aiosqlite:///:memory:'


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


# Override the `get_file_saver` to don't save files to hard disk
def mock_file_saver():
    return FileSaver(use_memory=True)


# Apply the override to FastAPI app
app.dependency_overrides[get_session] = override_get_session
app.dependency_overrides[get_file_saver] = mock_file_saver

transport = ASGITransport(app=app)


@pytest.fixture
def test_user_data():
    return {
        'email': 'newer@mail.com',
        'password': 'Q16werty!23',
        'first_name': 'newer',
        'last_name': 'newer',
        'sex': 'male',
        'birth_date': '2001-01-01',
    }


@pytest.fixture
def test_file():
    image = Image.new('RGB', (100, 100), color=(73, 109, 137))
    in_memory_file = io.BytesIO()
    image.save(in_memory_file, format='JPEG')
    in_memory_file.name = 'test_image.jpg'

    # Reset the file pointer to the beginning of the file
    in_memory_file.seek(0)
    return in_memory_file


@pytest.fixture
def multiple_test_users():
    return [
        {
            'email': 'newer1@mail.com',
            'password': 'Q16werty!23',
            'first_name': 'newer1',
            'last_name': 'newer1',
            'sex': 'male',
            'birth_date': '2001-01-01',
        },
        {
            'email': 'newer2@mail.com',
            'password': 'Q16werty!23',
            'first_name': 'newer2',
            'last_name': 'newer2',
            'sex': 'male',
            'birth_date': '2000-02-02',
        },
        {
            'email': 'newer3@mail.com',
            'password': 'Q16werty!23',
            'first_name': 'newer3',
            'last_name': 'newer3',
            'sex': 'female',
            'birth_date': '1999-03-03',
        },
    ]


@pytest.mark.asyncio
async def test_create_contact(test_user_data, test_file):
    async with AsyncClient(
        transport=transport,
        base_url='http://test',
    ) as client:
        files = {
            'in_file': (test_file.name, test_file, 'image/jpeg'),
        }

        response = await client.post(
            f'{API_URL}/auth/clients/create', params=test_user_data, files=files
        )

        assert (
            response.status_code == status.HTTP_201_CREATED
        ), f'Error: {response.json()}'
        print(response.json())


@pytest.mark.asyncio
async def test_create_same_contact(test_user_data, test_file):
    async with AsyncClient(
        transport=transport,
        base_url='http://test',
    ) as client:
        files = {
            'in_file': (test_file.name, test_file, 'image/jpeg'),
        }

        response = await client.post(
            f'{API_URL}/auth/clients/create', params=test_user_data, files=files
        )
        data = response.json()

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert data['detail'] == 'Email already taken'


@pytest.mark.asyncio
async def test_create_multiple_contacts(multiple_test_users, test_file):
    async with AsyncClient(
        transport=transport,
        base_url='http://test',
    ) as client:
        for user in multiple_test_users:
            files = {
                'in_file': (test_file.name, test_file, 'image/jpeg'),
            }

            response = await client.post(
                f'{API_URL}/auth/clients/create', params=user, files=files
            )

            assert response.status_code == status.HTTP_201_CREATED


@pytest.mark.asyncio
async def test_get_token_and_protected_endpoint():
    login_payload = {
        'email': 'newer@mail.com',
        'password': 'Q16werty!23',
    }

    async with AsyncClient(
        transport=transport,
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

        assert protected_response.status_code == status.HTTP_200_OK
