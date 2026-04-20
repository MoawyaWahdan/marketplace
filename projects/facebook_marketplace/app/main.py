from fastapi import FastAPI
from app.db.database import create_db_and_tables
from app.api.routes import users, listings, auth

app = FastAPI()

@app.on_event("startup")
def on_startup():
    create_db_and_tables()

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(listings.router)