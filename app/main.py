from fastapi import FastAPI
from app.db.database import create_db_and_tables
from app.api.routes import users, listings, auth
from contextlib import asynccontextmanager
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from app.core.config import LISTINGS_IMAGES_PATH
import os

app = FastAPI(
    title="Marketplace API",
    description="API for managing listings and users",
    version="1.0.0",
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    os.makedirs(LISTINGS_IMAGES_PATH, exist_ok=True)
    yield


app = FastAPI(lifespan=lifespan)


app.include_router(auth.router)
app.include_router(users.router)
app.include_router(listings.router)

app.mount("/static", StaticFiles(directory="app/static"), name="static")


@app.get("/")
def root():
    return RedirectResponse(url="/static/login.html")
