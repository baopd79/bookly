# src/books/routes.py
from fastapi import APIRouter, Query, status, Depends
from sqlmodel.ext.asyncio.session import AsyncSession
from src.auth.dependencies import get_current_user, require_admin
from src.db.main import get_session
from src.books.service import BookService
from src.books.schemas import BookCreateModel, BookUpdateModel, BookResponseModel
from src.errors import BookNotFoundException

import uuid


book_router = APIRouter()
book_service = BookService()


from fastapi import Query


@book_router.get("/", response_model=list[BookResponseModel])
async def get_all_books(
    session: AsyncSession = Depends(get_session),
    current_user=Depends(get_current_user),
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=10, le=100),
):
    skip = (page - 1) * limit
    return await book_service.get_all_books(session, skip, limit)


@book_router.post(
    "/", status_code=status.HTTP_201_CREATED, response_model=BookResponseModel
)
async def create_book(
    book_data: BookCreateModel,
    session: AsyncSession = Depends(get_session),
    admin_user=Depends(require_admin),
):
    return await book_service.create_book(book_data, session)


@book_router.get("/{book_uid}", response_model=BookResponseModel)
async def get_book_by_uid(
    book_uid: uuid.UUID,
    session: AsyncSession = Depends(get_session),
    current_user=Depends(get_current_user),
):
    book = await book_service.get_book_by_uid(book_uid, session)
    if not book:
        raise BookNotFoundException()
    return book


# update a book
# sử dụng patch để update một phần thông tin của book, nếu muốn update toàn bộ thông tin thì dùng put
@book_router.patch("/{book_uid}", response_model=BookResponseModel)
async def update_book_patch(
    book_uid: uuid.UUID,
    updated_book_data: BookUpdateModel,
    session: AsyncSession = Depends(get_session),
    admin_user=Depends(require_admin),
):
    book = await book_service.update_book(book_uid, updated_book_data, session)
    if not book:
        raise BookNotFoundException()
    return book


@book_router.delete("/{book_uid}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_book(
    book_uid: uuid.UUID,
    session: AsyncSession = Depends(get_session),
    admin_user=Depends(require_admin),
):
    book = await book_service.delete_book(book_uid, session)
    if not book:
        raise BookNotFoundException()
