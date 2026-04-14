from fastapi import FastAPI
from src.books.routes import book_router
from contextlib import asynccontextmanager
from src.db.main import init_db
from src.auth.routes import auth_router


@asynccontextmanager
async def lifespan(app: FastAPI):

    # Perform any startup tasks here (e.g., connect to the database)
    print("Starting up...")
    await init_db()  # Initialize the database (e.g., create tables, extensions, etc.)
    yield
    # Perform any shutdown tasks here (e.g., disconnect from the database)
    print("Shutting down...")


version = "v1"
app = FastAPI(
    version=version,
    title="Bookly API",
    description="A simple API for managing books",
    lifespan=lifespan,
)
app.include_router(book_router, prefix=f"/api/{version}/books", tags=["Books"])
app.include_router(auth_router, prefix=f"/api/{version}/auth", tags=["Auth"])
