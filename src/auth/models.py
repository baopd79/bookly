from sqlmodel import SQLModel, Field, Column, func
import sqlalchemy.dialects.postgresql as pg
import uuid
from datetime import datetime, date


class User(SQLModel, table=True):
    __tablename__ = "user_accounts"

    uid: uuid.UUID = Field(
        sa_column=Column(
            pg.UUID,
            primary_key=True,
            unique=True,
            nullable=False,
            default=uuid.uuid4,
        )
    )
    username: str
    email: str
    first_name: str
    last_name: str
    birthday: date = Field(sa_column=Column(pg.DATE, nullable=True))

    role: str = Field(
        sa_column=Column(pg.VARCHAR, nullable=False, server_default="user")
    )
    is_verified: bool = Field(default=False)
    password_hash: str = Field(exclude=True)
    created_at: datetime = Field(
        sa_column=Column(pg.TIMESTAMP, server_default=func.now())
    )
    updated_at: datetime = Field(
        sa_column=Column(pg.TIMESTAMP, server_default=func.now(), onupdate=func.now())
    )

    def __repr__(self) -> str:
        return f"<User {self.username}>"
