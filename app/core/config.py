import os
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

LISTINGS_IMAGES_PATH = "app/static/images/listing_images"
LISTINGS_IMAGES_URL_PATH = "/static/images/listing_images"
