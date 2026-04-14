# src/auth/schemas.py

Route → biết về HTTP (request, response, status code)
Service → biết về business logic (hash password, kiểm tra email)

Tách ra → dễ test, dễ tái sử dụng
→ service có thể dùng ở nhiều route khác nhau
→ route không cần biết DB hoạt động thế nào

```python
# src/auth/service.py
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select
from src.auth.models import User
from src.auth.schemas import UserCreateModel
from passlib.context import CryptContext
import uuid
from datetime import datetime


# CryptContext — quản lý thuật toán hash
# schemes=["bcrypt"] → dùng bcrypt
# deprecated="auto" → tự động upgrade hash cũ lên thuật toán mới hơn
passwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def generate_passwd_hash(password: str) -> str:
    """
    Hash plain text password
    "mypassword" → "$2b$12$..."
    Mỗi lần hash ra kết quả khác nhau nhờ salt tự động
    """
    return passwd_context.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    """
    So sánh plain text với hash
    Dùng khi login — không cần biết password gốc
    chỉ cần verify đúng không
    """
    return passwd_context.verify(password, password_hash)


class UserService:

    async def get_user_by_email(self, email: str, session: AsyncSession):
        """
        Tìm user theo email
        Dùng khi: login, kiểm tra email tồn tại, forgot password
        Trả None nếu không tìm thấy — route tự xử lý 404
        """
        statement = select(User).where(User.email == email)
        result = await session.exec(statement)
        return result.first()

    async def get_user_by_uid(self, uid: uuid.UUID, session: AsyncSession):
        """Tìm user theo uid — dùng khi lấy profile"""
        statement = select(User).where(User.uid == uid)
        result = await session.exec(statement)
        return result.first()

    async def user_exists(self, email: str, session: AsyncSession) -> bool:
        """
        Kiểm tra email đã tồn tại chưa
        Tách thành hàm riêng để tái sử dụng
        """
        user = await self.get_user_by_email(email, session)
        return user is not None

    async def create_user(self, user_data: UserCreateModel, session: AsyncSession):
        """
        Tạo user mới:
        1. Kiểm tra email chưa tồn tại
        2. Hash password — không bao giờ lưu plain text
        3. Lưu vào DB
        4. Trả về user object (không có password_hash nhờ exclude=True)
        """
        if await self.user_exists(user_data.email, session):
            return None

        user_dict = user_data.model_dump()

        new_user = User(
            uid=uuid.uuid4(),
            username=user_dict["username"],
            email=user_dict["email"],
            first_name=user_dict["first_name"],
            last_name=user_dict["last_name"],
            password_hash=generate_passwd_hash(user_dict["password"]),
        )

        session.add(new_user)
        await session.commit()
        await session.refresh(new_user)
        return new_user
```

Bước 3 — src/auth/routes.py
Lý thuyết — APIRouter prefix
python# Cách 1 — prefix trong **init**.py
router = APIRouter()
@router.post("/") # → /api/v1/auth/
@router.post("/login") # → /api/v1/auth/login

# Cách 2 — prefix trong router

router = APIRouter(prefix="/auth")
@router.post("/") # → /auth/
Cách 1 linh hoạt hơn — prefix quản lý tập trung ở **init**.py.

```python
# src/auth/routes.py
from fastapi import APIRouter, HTTPException, status, Depends
from sqlmodel.ext.asyncio.session import AsyncSession
from src.db.main import get_session
from src.auth.service import UserService
from src.auth.schemas import UserCreateModel, UserResponseModel

auth_router = APIRouter()
user_service = UserService()


@auth_router.post(
    "/signup",
    response_model=UserResponseModel,
    status_code=status.HTTP_201_CREATED
)
async def create_user_account(
    user_data: UserCreateModel,
    session: AsyncSession = Depends(get_session)
):
    """
    Đăng ký tài khoản mới:
    - Validate email format (EmailStr)
    - Validate password strength (field_validator)
    - Kiểm tra email chưa tồn tại
    - Hash password
    - Tạo user trong DB
    """
    user = await user_service.create_user(user_data, session)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Email {user_data.email} đã được sử dụng"
        )
    return user
```

Bước 4 — Đăng ký router trong src/**init**.py

```python

# src/__init__.py
from fastapi import FastAPI
from contextlib import asynccontextmanager
from src.db.main import init_db
from src.books.routes import book_router
from src.auth.routes import auth_router    # ✅ thêm


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Starting up...")
    await init_db()
    yield
    print("Shutting down...")


app = FastAPI(
    lifespan=lifespan,
    title="Bookly API",
    version="v1",
    description="API quản lý sách"
)

app.include_router(book_router, prefix="/api/v1/books", tags=["Books"])
app.include_router(auth_router, prefix="/api/v1/auth", tags=["Auth"])  # ✅
```

Luồng đăng ký hoàn chỉnh
Client gửi POST /api/v1/auth/signup
{
"username": "baobun",
"email": "bao@example.com",
"password": "Password123",
"first_name": "Bao",
"last_name": "Bun"
}
↓
Pydantic validate:
email đúng format? ✅
password >= 8 ký tự, có hoa, có số? ✅
username >= 3 ký tự, chỉ chữ và số? ✅
↓
UserService.create_user():
email đã tồn tại? → 409 Conflict
hash password: "Password123" → "$2b$12$..."
lưu vào DB
↓
Server trả về 201:
{
"uid": "550e8400-...",
"username": "baobun",
"email": "bao@example.com",
"is_verified": false,
"created_at": "2024-01-01T12:00:00"
}
Thách thức nhỏ
Trước khi chạy, tự trả lời:

Tại sao response_model=UserResponseModel quan trọng ở đây?
Nếu không có field_validator trên password, điều gì có thể xảy ra?
Tại sao dùng 409 Conflict thay vì 400 Bad Request khi email đã tồn tại?

Cập nhật code rồi chạy fastapi dev src/**init**.py và test POST /api/v1/auth/signup trên /docs nhé!
