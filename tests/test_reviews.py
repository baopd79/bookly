import pytest
from fastapi import status


@pytest.mark.asyncio
class TestReviewRoutes:
    """Test review endpoints"""

    # Test get reviews by book
    async def test_get_reviews_by_book_success(self, client, auth_headers, test_book):
        """Test get reviews for a book"""
        response = await client.get(
            f"/api/v1/reviews/book/{test_book.uid}",
            headers=auth_headers,
        )
        assert response.status_code == status.HTTP_200_OK
        reviews = response.json()
        assert isinstance(reviews, list)

    async def test_get_reviews_requires_auth(self, client, test_book):
        """Test get reviews requires authentication"""
        response = await client.get(
            f"/api/v1/reviews/book/{test_book.uid}",
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    # Test create review
    async def test_create_review_success(self, client, auth_headers, test_book):
        """Test create review by authenticated user"""
        response = await client.post(
            "/api/v1/reviews/",
            json={
                "book_uid": str(test_book.uid),
                "rating": 5,
                "comment": "Great book!",
            },
            headers=auth_headers,
        )
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["rating"] == 5
        assert data["comment"] == "Great book!"
        assert data["book_uid"] == str(test_book.uid)

    async def test_create_review_invalid_rating(self, client, auth_headers, test_book):
        """Test create review with invalid rating"""
        response = await client.post(
            "/api/v1/reviews/",
            json={
                "book_uid": str(test_book.uid),
                "rating": 10,  # ← rating must be 1-5
                "comment": "Great book!",
            },
            headers=auth_headers,
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    async def test_create_review_requires_auth(self, client, test_book):
        """Test create review requires authentication"""
        response = await client.post(
            "/api/v1/reviews/",
            json={
                "book_uid": str(test_book.uid),
                "rating": 5,
                "comment": "Great book!",
            },
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    # Test update review
    async def test_update_review_success(
        self, client, auth_headers, test_book, test_user, async_session
    ):
        """Test update own review"""
        from src.reviews.models import Review

        # Create a review first
        review = Review(
            book_uid=test_book.uid,
            user_uid=test_user.uid,
            rating=4,
            comment="Good book",
        )
        async_session.add(review)
        await async_session.commit()
        await async_session.refresh(review)

        # Update the review
        response = await client.patch(
            f"/api/v1/reviews/{review.uid}",
            json={
                "rating": 5,
                "comment": "Actually great book!",
            },
            headers=auth_headers,
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["rating"] == 5
        assert data["comment"] == "Actually great book!"

    async def test_update_review_not_owner(
        self, client, auth_headers, test_book, test_user, test_admin, async_session
    ):
        """Test update other user's review (not authorized)"""
        from src.reviews.models import Review

        # Create a review by admin
        review = Review(
            book_uid=test_book.uid,
            user_uid=test_admin.uid,
            rating=4,
            comment="Admin review",
        )
        async_session.add(review)
        await async_session.commit()
        await async_session.refresh(review)

        # Try to update as regular user
        response = await client.patch(
            f"/api/v1/reviews/{review.uid}",
            json={"rating": 1},
            headers=auth_headers,  # ← test_user
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert "Not authorized to update this review" in response.json()["detail"]

    async def test_update_review_not_found(self, client, auth_headers):
        """Test update non-existent review"""
        import uuid

        fake_uid = uuid.uuid4()
        response = await client.patch(
            f"/api/v1/reviews/{fake_uid}",
            json={"rating": 5},
            headers=auth_headers,
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "Review not found" in response.json()["detail"]

    # Test delete review
    async def test_delete_review_success(
        self, client, auth_headers, test_book, test_user, async_session
    ):
        """Test delete own review"""
        from src.reviews.models import Review

        # Create a review first
        review = Review(
            book_uid=test_book.uid,
            user_uid=test_user.uid,
            rating=4,
            comment="Good book",
        )
        async_session.add(review)
        await async_session.commit()
        await async_session.refresh(review)

        # Delete the review
        response = await client.delete(
            f"/api/v1/reviews/{review.uid}",
            headers=auth_headers,
        )
        assert response.status_code == status.HTTP_204_NO_CONTENT

    async def test_delete_review_not_owner(
        self, client, auth_headers, test_book, test_user, test_admin, async_session
    ):
        """Test delete other user's review (not authorized)"""
        from src.reviews.models import Review

        # Create a review by admin
        review = Review(
            book_uid=test_book.uid,
            user_uid=test_admin.uid,
            rating=4,
            comment="Admin review",
        )
        async_session.add(review)
        await async_session.commit()
        await async_session.refresh(review)

        # Try to delete as regular user
        response = await client.delete(
            f"/api/v1/reviews/{review.uid}",
            headers=auth_headers,  # ← test_user
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert "Not authorized to delete this review" in response.json()["detail"]

    async def test_delete_review_as_admin(
        self, client, admin_auth_headers, test_book, test_user, async_session
    ):
        """Test delete any review as admin"""
        from src.reviews.models import Review

        # Create a review by user
        review = Review(
            book_uid=test_book.uid,
            user_uid=test_user.uid,
            rating=4,
            comment="User review",
        )
        async_session.add(review)
        await async_session.commit()
        await async_session.refresh(review)

        # Delete as admin
        response = await client.delete(
            f"/api/v1/reviews/{review.uid}",
            headers=admin_auth_headers,
        )
        assert response.status_code == status.HTTP_204_NO_CONTENT

    async def test_delete_review_not_found(self, client, auth_headers):
        """Test delete non-existent review"""
        import uuid

        fake_uid = uuid.uuid4()
        response = await client.delete(
            f"/api/v1/reviews/{fake_uid}",
            headers=auth_headers,
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "Review not found" in response.json()["detail"]
