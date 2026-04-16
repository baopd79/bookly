import time

from fastapi import FastAPI, Request
from src.books.routes import book_router
from contextlib import asynccontextmanager
from src.db.main import init_db
from src.auth.routes import auth_router
from src.reviews.routes import review_router
from fastapi.middleware.cors import CORSMiddleware


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
app.include_router(review_router, prefix=f"/api/{version}/reviews", tags=["Reviews"])


# CROS ORIGIN RESOURCE SHARING (CORS) MIDDLEWARE
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=[
        "*"
    ],  # Cho phép tất cả các phương thức HTTP (GET, POST, PUT, DELETE, v.v.)
    allow_headers=[
        "*"
    ],  # Cho phép tất cả các header (có thể điều chỉnh để chỉ cho phép một số header cụ thể)
)


# request timming middleware
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response
