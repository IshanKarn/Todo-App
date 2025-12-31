import jwt
from datetime import datetime, timedelta
from django.conf import settings
import bcrypt
import re

EMAIL_REGEX = r"^[\w\.-]+@[\w\.-]+\.\w+$"
ALGORITHM = "HS256"
ACCESS_EXPIRE_MIN = 60
REFRESH_EXPIRE_DAYS = 7


def create_token(payload, expire):
    data = payload.copy()
    data["exp"] = datetime.utcnow() + expire
    return jwt.encode(data, settings.SECRET_KEY, algorithm=ALGORITHM)


def create_access_token(user_id):
    return create_token({"user_id": user_id}, timedelta(minutes=ACCESS_EXPIRE_MIN))


def create_refresh_token(user_id):
    return create_token({"user_id": user_id}, timedelta(days=REFRESH_EXPIRE_DAYS))


def decode_token(token):
    return jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])


def hash_password(password):
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def verify_password(password, hashed):
    return bcrypt.checkpw(password.encode(), hashed.encode())


def is_valid_email(email: str) -> bool:
    return re.match(EMAIL_REGEX, email) is not None