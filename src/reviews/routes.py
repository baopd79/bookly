from fastapi import APIRouter, status, Depends
from sqlmodel.ext.asyncio.session import AsyncSession
from src.auth.dependencies import get_current_user, require_admin
from src.db.main import get_session
from src.reviews.service import ReviewService
from src.reviews.schemas import (
    ReviewCreateModel,
    ReviewUpdateModel,
    ReviewResponseModel,
)
from src.errors import ReviewNotFoundException, UnauthorizedReviewAccessException
import uuid


review_router = APIRouter()
review_service = ReviewService()


@review_router.get("/book/{book_uid}", response_model=list[ReviewResponseModel])
async def get_reviews_by_book_uid(
    book_uid: uuid.UUID,
    session: AsyncSession = Depends(get_session),
    current_user=Depends(get_current_user),
):
    return await review_service.get_reviews_by_book_uid(book_uid, session)


@review_router.post(
    "/", status_code=status.HTTP_201_CREATED, response_model=ReviewResponseModel
)
async def create_review(
    review_data: ReviewCreateModel,
    session: AsyncSession = Depends(get_session),
    current_user=Depends(get_current_user),
):
    return await review_service.create_review(review_data, current_user.uid, session)


@review_router.patch("/{review_uid}", response_model=ReviewResponseModel)
async def update_review(
    review_uid: uuid.UUID,
    updated_review_data: ReviewUpdateModel,
    session: AsyncSession = Depends(get_session),
    current_user=Depends(get_current_user),
):
    review = await review_service.get_review_by_uid(review_uid, session)
    if not review:
        raise ReviewNotFoundException()
    if review.user_uid != current_user.uid:
        raise UnauthorizedReviewAccessException("update")
    return await review_service.update_review(review_uid, updated_review_data, session)


@review_router.delete("/{review_uid}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_review(
    review_uid: uuid.UUID,
    session: AsyncSession = Depends(get_session),
    current_user=Depends(get_current_user),
):

    review = await review_service.get_review_by_uid(review_uid, session)
    if not review:
        raise ReviewNotFoundException()
    if review.user_uid != current_user.uid and current_user.role != "admin":
        raise UnauthorizedReviewAccessException("delete")
    await review_service.delete_review(review_uid, session)
