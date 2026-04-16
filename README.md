# Bookly API

REST API quản lý sách xây dựng với FastAPI, PostgreSQL, SQLModel.

## Tech Stack

- **Framework:** FastAPI
- **Database:** PostgreSQL 16
- **ORM:** SQLModel + SQLAlchemy (async)
- **Authentication:** JWT (access token + refresh token)
- **Migration:** Alembic
- **Containerization:** Docker + Docker Compose

---

## Features

- CRUD Books — tạo, đọc, cập nhật, xóa sách
- CRUD Reviews — người dùng đánh giá và bình luận sách
- Authentication — đăng ký, đăng nhập, refresh token
- RBAC — phân quyền theo role (admin / user)
- Pagination — phân trang danh sách sách
- Middleware — CORS, request timing
- Custom Error Handling — exception tập trung, response nhất quán

---

## Architecture

```
bookly/
├── src/
│   ├── __init__.py         # FastAPI app, routers, middleware
│   ├── config.py           # Environment variables
│   ├── errors.py           # Custom exceptions
│   ├── db/
│   │   └── main.py         # Database engine, session factory
│   ├── auth/
│   │   ├── models.py       # User model
│   │   ├── schemas.py      # Pydantic schemas
│   │   ├── service.py      # Business logic
│   │   ├── routes.py       # Auth endpoints
│   │   ├── dependencies.py # get_current_user, RoleChecker
│   │   └── utils.py        # JWT helpers
│   ├── books/
│   │   ├── models.py
│   │   ├── schemas.py
│   │   ├── service.py
│   │   └── routes.py
│   └── reviews/
│       ├── models.py
│       ├── schemas.py
│       ├── service.py
│       └── routes.py
├── migrations/             # Alembic migrations
├── tests/                  # Unit & integration tests
├── Dockerfile
├── docker-compose.yml
└── requirements.txt
```

---

## Getting Started

### Yêu cầu

- Python 3.13+
- PostgreSQL 16+

### Cài đặt local

```bash
# 1. Clone repository
git clone https://github.com/baopd79/bookly.git
cd bookly

# 2. Tạo virtual environment
python3 -m venv env
source env/bin/activate

# 3. Cài dependencies
pip install -r requirements.txt

# 4. Tạo file .env
cp .env.example .env
# Điền thông tin vào .env

# 5. Chạy migration
alembic upgrade head

# 6. Chạy server
fastapi dev src/__init__.py
```

---

## Docker

```bash
# 1. Tạo file .env.docker từ .env.example
cp .env.example .env.docker
# Điền thông tin vào .env.docker (DATABASE_URL dùng db thay vì localhost)

# 2. Chạy toàn bộ stack
docker compose up --build

# 3. Chạy migration
docker compose exec app alembic upgrade head
```

App chạy tại `http://localhost:8000`

API docs tại `http://localhost:8000/docs`

---

## Environment Variables

| Variable                      | Description                  | Example                                                |
| ----------------------------- | ---------------------------- | ------------------------------------------------------ |
| `DATABASE_URL`                | PostgreSQL connection string | `postgresql+asyncpg://user:pass@localhost:5432/bookly` |
| `SECRET_KEY`                  | JWT secret key               | `your-secret-key`                                      |
| `ALGORITHM`                   | JWT algorithm                | `HS256`                                                |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Access token expiry          | `30`                                                   |
| `REFRESH_TOKEN_EXPIRE_DAYS`   | Refresh token expiry         | `30`                                                   |

---

## API Endpoints

### Auth

| Method | Endpoint                | Description             | Auth |
| ------ | ----------------------- | ----------------------- | ---- |
| POST   | `/api/v1/auth/register` | Đăng ký tài khoản       | ❌   |
| POST   | `/api/v1/auth/login`    | Đăng nhập               | ❌   |
| POST   | `/api/v1/auth/refresh`  | Refresh access token    | ❌   |
| GET    | `/api/v1/auth/{uid}`    | Lấy thông tin user      | ✅   |
| PATCH  | `/api/v1/auth/{uid}`    | Cập nhật thông tin user | ✅   |

### Books

| Method | Endpoint              | Description                    | Auth     |
| ------ | --------------------- | ------------------------------ | -------- |
| GET    | `/api/v1/books`       | Danh sách sách (có pagination) | ✅ User  |
| POST   | `/api/v1/books`       | Tạo sách mới                   | ✅ Admin |
| GET    | `/api/v1/books/{uid}` | Chi tiết sách                  | ✅ User  |
| PATCH  | `/api/v1/books/{uid}` | Cập nhật sách                  | ✅ Admin |
| DELETE | `/api/v1/books/{uid}` | Xóa sách                       | ✅ Admin |

### Reviews

| Method | Endpoint                          | Description               | Auth             |
| ------ | --------------------------------- | ------------------------- | ---------------- |
| GET    | `/api/v1/reviews/book/{book_uid}` | Danh sách review của sách | ✅ User          |
| POST   | `/api/v1/reviews`                 | Tạo review                | ✅ User          |
| PATCH  | `/api/v1/reviews/{uid}`           | Cập nhật review           | ✅ Owner         |
| DELETE | `/api/v1/reviews/{uid}`           | Xóa review                | ✅ Owner / Admin |

---

## RBAC

| Role    | Quyền                                                        |
| ------- | ------------------------------------------------------------ |
| `user`  | Đọc sách, tạo/sửa/xóa review của mình                        |
| `admin` | Tất cả quyền của user + CRUD sách + xóa review của bất kỳ ai |
