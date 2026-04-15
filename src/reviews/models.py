from datetime import datetime
import uuid

from sqlmodel import Column, Field, SQLModel
import sqlalchemy.dialects.postgresql as pg


class Review(SQLModel, table=True):
    __tablename__ = "reviews"

    uid: uuid.UUID = Field(
        sa_column=Column(
            pg.UUID,
            primary_key=True,
            unique=True,
            nullable=False,
            default=uuid.uuid4,
        )
    )
    book_uid: uuid.UUID = Field(foreign_key="books.uid")
    user_uid: uuid.UUID = Field(foreign_key="user_accounts.uid")
    rating: int = Field(sa_column=Column(pg.INTEGER, nullable=False, default=5))
    comment: str | None = Field(default=None, nullable=True)
    created_at: datetime = Field(sa_column=Column(pg.TIMESTAMP, default=datetime.now))
    updated_at: datetime = Field(
        sa_column=Column(pg.TIMESTAMP, default=datetime.now, onupdate=datetime.now)
    )

    def __repr__(self) -> str:
        return f"<Review {self.rating} stars for book {self.book_uid}>"
