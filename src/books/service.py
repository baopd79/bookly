from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select
from src.books.models import Book
from src.db.main import engine
from src.books.schemas import BookCreateModel, BookUpdateModel, BookResponseModel
import uuid
from datetime import datetime


class BookService:
    # get all books
    async def get_all_books(
        self, session: AsyncSession, skip: int = 0, limit: int = 100
    ):
        statement = (
            select(Book).order_by(Book.created_at.desc()).offset(skip).limit(limit)
        )
        result = await session.exec(statement)
        return result.all()

    # get book by id
    async def get_book_by_uid(self, book_uid: uuid.UUID, session: AsyncSession):
        statement = select(Book).where(Book.uid == book_uid)
        result = await session.exec(statement)
        book = result.first()
        return book if book else None

    # create a new book
    async def create_book(self, book_data: BookCreateModel, session: AsyncSession):
        new_book = Book(**book_data.model_dump())
        new_book.uid = uuid.uuid4()
        session.add(new_book)
        await session.commit()
        await session.refresh(new_book)
        return new_book

    # update a book
    async def update_book(
        self, book_uid: uuid.UUID, update_data: BookUpdateModel, session: AsyncSession
    ):
        book = await self.get_book_by_id(book_uid, session)
        if not book:
            return None
        update_dict = update_data.model_dump(exclude_unset=True)
        for key, value in update_dict.items():
            setattr(book, key, value)
        book.updated_at = datetime.now()
        await session.commit()
        await session.refresh(book)
        return book

    # delete a book
    async def delete_book(self, book_uid: uuid.UUID, session: AsyncSession):
        book = await self.get_book_by_id(book_uid, session)
        if not book:
            return None
        await session.delete(book)
        await session.commit()
        return book
