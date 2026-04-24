from fastapi import FastAPI
from app.db.database import create_db_and_tables
from app.api.routes import users, listings, auth
from contextlib import asynccontextmanager


app = FastAPI(
    title="Marketplace API",
    description="API for managing listings and users",
    version="1.0.0",
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield


app = FastAPI(lifespan=lifespan)


app.include_router(auth.router)
app.include_router(users.router)
app.include_router(listings.router)
