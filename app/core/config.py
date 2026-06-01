import os
from dotenv import load_dotenv

load_dotenv()


def get_env_variable(key):
    value = os.getenv(key)
    if not value:
        raise ValueError(f"{key} is not set in environment variables")
    return value


SECRET_KEY = get_env_variable("SECRET_KEY")

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

DATABASE_URL = get_env_variable("DATABASE_URL")
if DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace(
        "postgresql://",
        "postgresql+psycopg://",
        1,
    )


AWS_ACCESS_KEY_ID = get_env_variable("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = get_env_variable("AWS_SECRET_ACCESS_KEY")
AWS_REGION = get_env_variable("AWS_REGION")
S3_BUCKET_NAME = get_env_variable("S3_BUCKET_NAME")
