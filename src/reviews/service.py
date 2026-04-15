from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select
from src.reviews.models import Review
from src.reviews.schemas import (
    ReviewCreateModel,
    ReviewUpdateModel,
    ReviewResponseModel,
)
import uuid
from datetime import datetime


class ReviewService:
    # get all reviews for a book
    async def get_reviews_by_book_uid(self, book_uid: uuid.UUID, session: AsyncSession):
        statement = (
            select(Review)
            .where(Review.book_uid == book_uid)
            .order_by(Review.created_at.desc())
        )
        result = await session.exec(statement)
        return result.all()

    # get review by uid
    async def get_review_by_uid(self, review_uid: uuid.UUID, session: AsyncSession):
        statement = select(Review).where(Review.uid == review_uid)
        result = await session.exec(statement)

        review = result.first()
        return review if review else None

    # create a new review
    async def create_review(
        self, review_data: ReviewCreateModel, user_uid: uuid.UUID, session: AsyncSession
    ):
        new_review = Review(**review_data.model_dump())
        new_review.uid = uuid.uuid4()
        new_review.user_uid = user_uid
        session.add(new_review)
        await session.commit()
        await session.refresh(new_review)
        return new_review

    # update a review
    async def update_review(
        self,
        review_uid: uuid.UUID,
        update_data: ReviewUpdateModel,
        session: AsyncSession,
    ):
        review = await self.get_review_by_uid(review_uid, session)
        if not review:
            return None
        update_dict = update_data.model_dump(exclude_unset=True)
        for key, value in update_dict.items():
            setattr(review, key, value)
        review.updated_at = datetime.now()
        await session.commit()
        await session.refresh(review)
        return review

    async def delete_review(self, review_uid: uuid.UUID, session: AsyncSession):
        review = await self.get_review_by_uid(review_uid, session)
        if not review:
            return None
        await session.delete(review)
        await session.commit()
        return review
