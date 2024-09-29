import uuid


async def get_new_user_id() -> uuid.UUID:
    # Generate a new user ID
    return uuid.uuid4()
