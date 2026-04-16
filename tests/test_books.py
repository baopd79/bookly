import pytest
from fastapi import status
from datetime import date


@pytest.mark.asyncio
class TestBookRoutes:
    """Test book endpoints"""

    # Test get all books
    async def test_get_all_books_success(self, client, auth_headers, test_book):
        """Test get all books"""
        response = await client.get(
            "/api/v1/books/",
            headers=auth_headers,
        )
        assert response.status_code == status.HTTP_200_OK
        books = response.json()
        assert len(books) > 0
        assert books[0]["title"] == "Test Book"

    async def test_get_all_books_requires_auth(self, client):
        """Test get all books without authentication"""
        response = await client.get("/api/v1/books/")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    # Test create book
    async def test_create_book_success(self, client, admin_auth_headers):
        """Test create book by admin"""
        response = await client.post(
            "/api/v1/books/",
            json={
                "title": "New Book",
                "author": "New Author",
                "publisher": "New Publisher",
                "published_date": "2023-01-01",
                "page_count": 250,
                "language": "en",
            },
            headers=admin_auth_headers,
        )
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["title"] == "New Book"
        assert data["author"] == "New Author"

    async def test_create_book_requires_admin(self, client, auth_headers):
        """Test create book requires admin role"""
        response = await client.post(
            "/api/v1/books/",
            json={
                "title": "New Book",
                "author": "New Author",
                "publisher": "New Publisher",
                "published_date": "2023-01-01",
                "page_count": 250,
                "language": "en",
            },
            headers=auth_headers,  # ← regular user
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert "Insufficient permissions" in response.json()["detail"]

    # Test get book by uid
    async def test_get_book_success(self, client, auth_headers, test_book):
        """Test get book by uid"""
        response = await client.get(
            f"/api/v1/books/{test_book.uid}",
            headers=auth_headers,
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["uid"] == str(test_book.uid)
        assert data["title"] == "Test Book"

    async def test_get_book_not_found(self, client, auth_headers):
        """Test get non-existent book"""
        import uuid

        fake_uid = uuid.uuid4()
        response = await client.get(
            f"/api/v1/books/{fake_uid}",
            headers=auth_headers,
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "Book not found" in response.json()["detail"]

    # Test update book
    async def test_update_book_success(self, client, admin_auth_headers, test_book):
        """Test update book by admin"""
        response = await client.patch(
            f"/api/v1/books/{test_book.uid}",
            json={
                "title": "Updated Title",
                "page_count": 400,
            },
            headers=admin_auth_headers,
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["title"] == "Updated Title"
        assert data["page_count"] == 400

    async def test_update_book_not_found(self, client, admin_auth_headers):
        """Test update non-existent book"""
        import uuid

        fake_uid = uuid.uuid4()
        response = await client.patch(
            f"/api/v1/books/{fake_uid}",
            json={"title": "Updated Title"},
            headers=admin_auth_headers,
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "Book not found" in response.json()["detail"]

    async def test_update_book_requires_admin(self, client, auth_headers, test_book):
        """Test update book requires admin role"""
        response = await client.patch(
            f"/api/v1/books/{test_book.uid}",
            json={"title": "Updated Title"},
            headers=auth_headers,  # ← regular user
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN

    # Test delete book
    async def test_delete_book_success(self, client, admin_auth_headers, test_book):
        """Test delete book by admin"""
        response = await client.delete(
            f"/api/v1/books/{test_book.uid}",
            headers=admin_auth_headers,
        )
        assert response.status_code == status.HTTP_204_NO_CONTENT

    async def test_delete_book_not_found(self, client, admin_auth_headers):
        """Test delete non-existent book"""
        import uuid

        fake_uid = uuid.uuid4()
        response = await client.delete(
            f"/api/v1/books/{fake_uid}",
            headers=admin_auth_headers,
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "Book not found" in response.json()["detail"]

    async def test_delete_book_requires_admin(self, client, auth_headers, test_book):
        """Test delete book requires admin role"""
        response = await client.delete(
            f"/api/v1/books/{test_book.uid}",
            headers=auth_headers,  # ← regular user
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN
