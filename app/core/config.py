import os
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    raise ValueError("SECRET_KEY is not set in environment variables")

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

LISTINGS_IMAGES_PATH = "app/static/images/listing_images"
LISTINGS_IMAGES_URL_PATH = "/static/images/listing_images"

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL is not set in environment variables")
