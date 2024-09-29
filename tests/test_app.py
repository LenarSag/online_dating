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

transport = ASGITransport(app=app)


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
def test_user_coordinates():
    return {'latitude': 11.345, 'longitude': 23.456}


@pytest.fixture
def test_user_with_bad_image_data():
    return {
        'email': 'file@mail.com',
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
def test_large_file():
    # 6MB file (1MB = 1024 * 1024 bytes)
    size_in_mb = 6
    large_data = b'a' * (size_in_mb * 1024 * 1024)  # Creates a file of 'a' characters

    in_memory_file = io.BytesIO(large_data)
    in_memory_file.name = (
        'large_image.jpg'  # Keep it as an image extension to check for file size error
    )
    in_memory_file.seek(0)
    return in_memory_file


@pytest.fixture
def test_non_image_file():
    in_memory_file = io.BytesIO(b'This is a text file, not an image.')
    in_memory_file.name = 'test_file.txt'
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


@pytest.fixture
def auth_headers(event_loop):
    async def get_headers():
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
            assert response.status_code == 200, f'Login failed: {response.json()}'

            login_data = response.json()
            access_token = login_data['access_token']

            return {
                'Authorization': f'Bearer {access_token}',
            }

    return event_loop.run_until_complete(get_headers())


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
        response_data = response.json()

        assert (
            test_user_data['email'] == response_data['email']
        ), f"Expected email: {test_user_data['email']}, but got: {response_data['email']}"
        assert (
            test_user_data['first_name'] == response_data['first_name']
        ), f"Expected first name: {test_user_data['first_name']}, but got: {response_data['first_name']}"
        assert (
            test_user_data['last_name'] == response_data['last_name']
        ), f"Expected last name: {test_user_data['last_name']}, but got: {response_data['last_name']}"
        assert (
            test_user_data['sex'] == response_data['sex']
        ), f"Expected sex: {test_user_data['sex']}, but got: {response_data['sex']}"
        assert (
            test_user_data['birth_date'] == response_data['birth_date']
        ), f"Expected birth_date: {test_user_data['birth_date']}, but got: {response_data['birth_date']}"


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

        assert (
            response.status_code == status.HTTP_400_BAD_REQUEST
        ), f'Error: {response.json()}'
        expected_error_message = 'Email already taken'
        assert data['detail'] == expected_error_message


@pytest.mark.asyncio
async def test_create_contact_with_big_image(
    test_user_with_bad_image_data, test_large_file
):
    async with AsyncClient(
        transport=transport,
        base_url='http://test',
    ) as client:
        files = {
            'in_file': (test_large_file.name, test_large_file, 'image/jpeg'),
        }

        response = await client.post(
            f'{API_URL}/auth/clients/create',
            params=test_user_with_bad_image_data,
            files=files,
        )

        assert (
            response.status_code == status.HTTP_400_BAD_REQUEST
        ), f'Error: {response.json()}'
        expected_error_message = 'File is too big'
        assert (
            response.json()['detail'] == expected_error_message
        ), f"Expected: '{expected_error_message}', got: '{response.json()['detail']}'"


@pytest.mark.asyncio
async def test_create_contact_with_non_image(
    test_user_with_bad_image_data, test_non_image_file
):
    async with AsyncClient(
        transport=transport,
        base_url='http://test',
    ) as client:
        files = {
            'in_file': (test_non_image_file.name, test_non_image_file, 'text/txt'),
        }

        response = await client.post(
            f'{API_URL}/auth/clients/create',
            params=test_user_with_bad_image_data,
            files=files,
        )

        assert (
            response.status_code == status.HTTP_400_BAD_REQUEST
        ), f'Error: {response.json()}'

        # Assert that the error message is as expected
        expected_error_message = 'You can upload only images'
        assert (
            response.json()['detail'] == expected_error_message
        ), f"Expected: '{expected_error_message}', got: '{response.json()['detail']}'"


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

            assert (
                response.status_code == status.HTTP_201_CREATED
            ), f'Error: {response.json()}'


@pytest.mark.asyncio
async def test_get_protected_endpoint(auth_headers):
    async with AsyncClient(
        transport=transport,
        base_url='http://test',
    ) as client:
        response = await client.get(
            f'{API_URL}/clients/',
            headers=auth_headers,
        )

        assert response.status_code == status.HTTP_200_OK


@pytest.mark.asyncio
async def test_update_coordinates(auth_headers, test_user_coordinates):
    async with AsyncClient(
        transport=transport,
        base_url='http://test',
    ) as client:
        response = await client.post(
            f'{API_URL}/clients/update_coordinates',
            headers=auth_headers,
            json=test_user_coordinates,
        )

        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()
        assert (
            test_user_coordinates['latitude'] == response_data['location']['latitude']
        ), f"Expected latitude: { test_user_coordinates['latitude']}, but got: {response_data['location']['latitude']}"
        assert (
            test_user_coordinates['longitude'] == response_data['location']['longitude']
        ), f"Expected longitude: { test_user_coordinates['longitude']}, but got: {response_data['location']['longitude']}"
