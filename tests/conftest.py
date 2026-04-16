import pytest
from httpx import AsyncClient, ASGITransport
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker
from src.__init__ import app
from src.db.main import get_session
from src.config import Config


# Tạo engine kết nối tới database test
test_engine = create_async_engine(Config.DATABASE_TEST_URL, echo=True, future=True)


# Tạo fixture cho session test
# giải thích : fixture này sẽ tạo một session mới kết nối tới database test trước mỗi test function, và sau khi test function hoàn thành thì session sẽ tự động đóng lại. Điều này giúp đảm bảo rằng mỗi test function sẽ có một môi trường database sạch sẽ và không bị ảnh hưởng bởi các test function khác. Bạn có thể sử dụng fixture này trong các test function của mình bằng cách thêm tham số test_session vào hàm test, ví dụ: async def test_create_book(test_session: AsyncSession): ...
@pytest.fixture(scope="session")
async def test_session():
    # Tạo session factory
    TestSession = sessionmaker(
        bind=test_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    async with TestSession() as session:
        yield session


# Tạo fixture cho client test
# giải thích : fixture này sẽ tạo một AsyncClient mới sử dụng ASGITransport để kết nối trực tiếp tới ứng dụng FastAPI của bạn mà không cần phải chạy server. Điều này giúp cho việc test các route của bạn trở nên nhanh chóng và hiệu quả hơn.
@pytest.fixture(scope="session")
async def test_client(test_session):
    async def override_get_session():
        yield test_session

    app.dependency_overrides[get_session] = override_get_session
    async with AsyncClient(
        transport=ASGITransport(app), base_url="http://test"
    ) as client:
        yield client
    app.dependency_overrides.clear()
