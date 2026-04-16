# Testing Guide for Bookly

## Setup

Đã cài đặt:

```bash
pip install pytest pytest-asyncio httpx
```

## Project Structure

```
tests/
├── __init__.py
├── conftest.py          # Shared fixtures (database, client, users)
├── test_auth.py         # Auth endpoint tests
├── test_books.py        # Book endpoint tests
└── test_reviews.py      # Review endpoint tests
```

## Running Tests

**Run tất cả tests:**

```bash
pytest
```

**Run tests từ một file cụ thể:**

```bash
pytest tests/test_auth.py
```

**Run tests từ một class cụ thể:**

```bash
pytest tests/test_auth.py::TestAuthRoutes
```

**Run một test cụ thể:**

```bash
pytest tests/test_auth.py::TestAuthRoutes::test_register_success
```

**Run với verbose output:**

```bash
pytest -v
```

**Run với coverage:**

```bash
pip install pytest-cov
pytest --cov=src tests/
```

## Test Coverage

| Module    | Tests | Coverage                                 |
| --------- | ----- | ---------------------------------------- |
| `auth`    | 11    | register, login, refresh token, get user |
| `books`   | 10    | create, read, update, delete (with auth) |
| `reviews` | 10    | create, read, update, delete (with auth) |

## Fixtures

### Database & Session

- `async_engine` - Async SQLite in-memory engine
- `async_session_maker` - AsyncSession factory
- `async_session` - Async session instance

### Client & Auth

- `client` - AsyncClient for making HTTP requests
- `auth_headers` - Auth headers cho user
- `admin_auth_headers` - Auth headers cho admin

### Test Data

- `test_user` - Regular user (test@example.com / Test1234)
- `test_admin` - Admin user (admin@example.com / Admin1234)
- `test_book` - Test book

## Notes

- Tests dùng SQLite in-memory database (không ảnh hưởng database thực)
- Mỗi test được chạy trong transaction riêng (isolated)
- Async/await được support tự động bằng `pytest-asyncio`
- Custom exceptions được test để đảm bảo return đúng status code
