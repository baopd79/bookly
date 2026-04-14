Tổng hợp kiến thức đã học

1. Kiến trúc tổng thể
   Client (Postman/Browser)
   ↓ HTTP Request
   FastAPI App (src/**init**.py)
   ↓ route matching
   Router (routes.py)
   ↓ Depends(get_session) inject session
   ↓ gọi service
   Service (service.py)
   ↓ query DB
   Database (PostgreSQL)
   ↓ trả data
   Service → Router → Client

2. Vai trò từng folder/file
   Cấu trúc hiện tại
   bookly/
   ├── .env ← biến môi trường, secrets — không commit git
   ├── alembic.ini ← config Alembic
   ├── migrations/ ← lịch sử thay đổi DB
   │ ├── env.py ← entry point Alembic, kết nối DB
   │ ├── script.py.mako ← template tạo migration file
   │ └── versions/ ← các file migration theo thứ tự thời gian
   │
   └── src/
   ├── **init**.py ← khởi tạo FastAPI app, đăng ký routers, lifespan
   ├── config.py ← đọc biến môi trường từ .env vào Python
   │
   ├── db/
   │ └── main.py ← tạo engine kết nối DB, get_session factory
   │
   ├── books/
   │ ├── models.py ← SQLModel table — Book
   │ ├── schemas.py ← Pydantic models — BookCreate, BookResponse
   │ ├── service.py ← business logic — CRUD book
   │ └── routes.py ← endpoints — GET/POST/PATCH/DELETE /books
   │
   ├── auth/
   │ ├── models.py ← SQLModel table — User
   │ ├── schemas.py ← Pydantic models — UserCreate, UserResponse
   │ ├── service.py ← business logic — hash password, CRUD user
   │ └── routes.py ← endpoints — /register, /login
   │
   └── reviews/
   └── models.py ← SQLModel table — Review

Vai trò chi tiết từng file
.env
Lưu thông tin nhạy cảm:
DATABASE_URL=postgresql+asyncpg://...
SECRET_KEY=...

Không bao giờ commit lên git
.env.example → file mẫu để share với team
src/**init**.py
python# 3 nhiệm vụ chính:

# 1. Khởi tạo FastAPI app

app = FastAPI(title="Bookly", version="v1")

# 2. Quản lý lifespan — chạy khi server start/stop

@asynccontextmanager
async def lifespan(app):
await init_db() # start
yield # stop

# 3. Đăng ký routers

app.include_router(book_router, prefix="/api/v1/books")
app.include_router(auth_router, prefix="/api/v1/auth")
src/config.py
python# Đọc .env vào Python object
class Settings(BaseSettings):
DATABASE_URL: str
model_config = SettingsConfigDict(env_file=".env")

Config = Settings()

# Dùng: Config.DATABASE_URL

src/db/main.py
python# 2 nhiệm vụ:

# 1. Tạo engine — connection pool đến PostgreSQL

engine = AsyncEngine(create_engine(url=Config.DATABASE_URL))

# 2. get_session — factory tạo session cho mỗi request

async def get_session() -> AsyncSession:
async with Session() as session:
yield session # Depends() dùng cái này
models.py — mỗi module có riêng
python# Đại diện cho TABLE trong PostgreSQL
class Book(SQLModel, table=True):
**tablename** = "books"
uid: uuid.UUID # cột trong DB
title: str # cột trong DB
created_at: datetime # cột trong DB

# Khi có thay đổi → tạo Alembic migration

schemas.py — mỗi module có riêng
python# Đại diện cho DATA CLIENT GỬI/NHẬN — không liên quan DB

# Input — client gửi lên

class BookCreateModel(BaseModel):
title: str # client phải gửi # ❌ không có uid, created_at — server tự tạo

# Output — server trả về

class BookResponseModel(BaseModel):
uid: uuid.UUID # server tạo
title: str
created_at: datetime # ❌ không có password_hash
service.py — mỗi module có riêng
python# Toàn bộ business logic + tương tác DB
class BookService:
async def get_all(session): # SELECT \* FROM books
async def get_by_uid(uid, session): # SELECT WHERE uid=
async def create(data, session): # INSERT INTO books
async def update(uid, data, session): # UPDATE books SET
async def delete(uid, session): # DELETE FROM books
routes.py — mỗi module có riêng
python# Nhận HTTP request → gọi service → trả response

# KHÔNG chứa business logic

@router.get("/", response_model=list[BookResponseModel])
async def get_all_books(session = Depends(get_session)):
return await book_service.get_all(session) # ↑ gọi service, không tự query DB

3. Workflow chi tiết
   Models → Schemas → Service → Routes
   ┌─────────────────────────────────────────────────────┐
   │ models.py │
   │ Định nghĩa cấu trúc DB │
   │ class Book(SQLModel, table=True) │
   │ uid, title, author, created_at... │
   └─────────────────┬───────────────────────────────────┘
   │ dùng để
   ▼
   ┌─────────────────────────────────────────────────────┐
   │ schemas.py │
   │ Định nghĩa data API │
   │ BookCreateModel ← client gửi lên (không có uid) │
   │ BookResponseModel← server trả về (không có pass) │
   │ BookUpdateModel ← PATCH (tất cả Optional) │
   └─────────────────┬───────────────────────────────────┘
   │ dùng để
   ▼
   ┌─────────────────────────────────────────────────────┐
   │ service.py │
   │ Xử lý business logic │
   │ - Validate nghiệp vụ (email đã tồn tại chưa?) │
   │ - Hash password trước khi lưu │
   │ - Query DB bằng SQLModel select() │
   │ - add → commit → refresh │
   └─────────────────┬───────────────────────────────────┘
   │ được gọi bởi
   ▼
   ┌─────────────────────────────────────────────────────┐
   │ routes.py │
   │ Nhận request, trả response │
   │ - Depends(get_session) inject session tự động │
   │ - Gọi service │
   │ - Raise HTTPException nếu lỗi │
   │ - response_model lọc data trả về │
   └─────────────────────────────────────────────────────┘

4. Workflow một request thực tế
   POST /api/v1/auth/register
5. Client gửi:
   POST /api/v1/auth/register
   Body: {"username": "baobun", "email": "...", "password": "..."}

6. FastAPI nhận request
   → tìm route khớp: auth_router.post("/register")

7. Pydantic validate (UserCreateModel):
   → email đúng format? ✅
   → password >= 8 ký tự, có hoa, có số? ✅
   → Nếu sai → 422 Unprocessable Entity tự động

8. Depends(get_session):
   → tạo AsyncSession mới
   → truyền vào hàm register_user

9. Route gọi service:
   user = await user_service.create_user(user_data, session)

10. Service xử lý:
    → user_exist() kiểm tra email → 409 nếu có
    → generate_passwd_hash() hash password
    → User() tạo object
    → session.add() → commit() → refresh()

11. Route kiểm tra kết quả:
    → None → raise 409 Conflict
    → User object → return

12. FastAPI serialize (UserResponseModel):
    → lọc bỏ password_hash
    → convert UUID, datetime → string JSON

13. Client nhận:
    201 Created
    {"uid": "...", "username": "baobun", "email": "...", ...}

# 5. Các concept quan trọng

Dependency Injection
python# Depends(get_session) — FastAPI tự động:

# 1. Gọi get_session

# 2. Tạo session mới cho mỗi request

# 3. Truyền vào hàm

# 4. Đóng session sau khi hàm xong

async def get_all(session: AsyncSession = Depends(get_session)):
...

1. Password Security

Plain text → bcrypt hash (1 chiều, không reverse được)
Login: compare plain text với hash — không cần biết password gốc
bcrypt có salt tự động → cùng password, hash khác nhau mỗi lần

2. Pydantic Validation
   field_validator → validate từng field riêng lẻ
   model_validator → validate nhiều field cùng lúc
   EmailStr → validate email format tự động
   exclude=True → field này không bao giờ xuất hiện trong response
   exclude_unset=True → chỉ lấy field được gửi lên (dùng cho PATCH)

3. Alembic Migration

create_all → chỉ tạo table mới, không sửa table cũ
Alembic → track toàn bộ thay đổi DB như Git
có thể upgrade và downgrade
data cũ vẫn còn sau khi migrate

4. SQLModel
   table=True → class này là DB table
   table=False → class này chỉ là Pydantic model (default)
   Field(foreign_key="books.uid") → ràng buộc FK với table khác
   Field(exclude=True) → không xuất hiện trong response

5. Nguyên tắc quan trọng nhớ mãi

6. Route không biết về DB — chỉ gọi service
7. Service không biết về HTTP — chỉ xử lý logic
8. Models = DB structure, Schemas = API structure
9. Không bao giờ lưu plain text password
10. Không bao giờ trả password_hash về client
11. response_model là lớp bảo vệ cuối cùng
12. exclude_unset=True cho PATCH — không ghi đè data cũ
13. Foreign key đảm bảo tính toàn vẹn dữ liệu
