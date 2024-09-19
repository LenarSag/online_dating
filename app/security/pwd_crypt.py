from passlib.context import CryptContext


pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')


def verify_password(plain_code, hashed_code):
    return pwd_context.verify(plain_code, hashed_code)


def get_hashed_password(password):
    return pwd_context.hash(password)
