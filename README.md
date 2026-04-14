# Bookly API

API quản lý sách xây dựng với FastAPI, PostgreSQL, SQLModel.

## Yêu cầu

- Python 3.13+
- PostgreSQL 16+

## Cài đặt

1. Clone repository
   git clone https://github.com/username/bookly.git
   cd bookly

2. Tạo virtual environment
   python3 -m venv env
   source env/bin/activate

3. Cài dependencies
   pip install -r requirements.txt

4. Tạo file .env từ .env.example
   cp .env.example .env

# Điền thông tin DB vào .env

5. Chạy migration
   alembic upgrade head

6. Chạy server
   fastapi dev src/**init**.py

## API Endpoints

### Books

- GET /api/v1/books
- POST /api/v1/books
- GET /api/v1/books/{uid}
- PATCH /api/v1/books/{uid}
- DELETE /api/v1/books/{uid}

### Auth

- POST /api/v1/auth/register
- GET /api/v1/auth/{uid}
- PATCH /api/v1/auth/{uid}
