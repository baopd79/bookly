from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select
from src.auth.models import User
from src.auth.schemas import UserCreateModel, UserUpdateModel, TokenResponseModel
from passlib.context import CryptContext
import uuid
from datetime import datetime, timedelta
from src.auth.utils import create_access_token, decode_token

from src.config import Config


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

    # tìm user theo id dùng khi lấy profile
    async def get_user_by_uid(self, uid: uuid.UUID, session: AsyncSession):
        statement = select(User).where(User.uid == uid)
        result = await session.exec(statement)
        return result.first()

    # check email ton tai chua
    async def user_exist(self, email: str, session: AsyncSession) -> bool:
        user = await self.get_user_by_email(email, session)
        return user is not None

    # tao moi user
    async def create_user(self, user_data: UserCreateModel, session: AsyncSession):
        """
        Tạo user mới:
        1. Kiểm tra email chưa tồn tại
        2. Hash password — không bao giờ lưu plain text
        3. Lưu vào DB
        4. Trả về user object (không có password_hash nhờ exclude=True)
        """
        if await self.user_exist(user_data.email, session):
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

    # cap nhat thong tin user
    async def update_user(
        self, uid: uuid.UUID, update_data: UserUpdateModel, session: AsyncSession
    ):
        # tim user
        user = await self.get_user_by_uid(uid, session)
        if not user:
            return None

        # cap nhat tung field duoc gui len
        update_dict = update_data.model_dump(exclude_unset=True)
        for key, value in update_dict.items():
            setattr(user, key, value)
        await session.commit()
        await session.refresh(user)
        return user

    # hàm login_user có luồng tìm user theo email, nếu không tìm thấy trả về None, nếu tìm thấy thì verify password, nếu verify thất bại trả về None, nếu verify thành công thì tạo access token và refresh token rồi trả về TokenResponseModel chứa 2 token này cùng thông tin user (có thể là UserResponseModel hoặc dict tuỳ theo nhu cầu) để client dùng sau này khi gọi API cần xác thực.
    async def login_user(
        self, email: str, password: str, session: AsyncSession
    ) -> TokenResponseModel | None:
        user = await self.get_user_by_email(email, session)
        if not user:
            return None
        if not verify_password(password, user.password_hash):
            return None
        user_data = {
            "uid": str(user.uid),
            "email": user.email,
            "username": user.username,
            "role": user.role,
        }
        access_token = create_access_token(user_data, refresh=False)
        refresh_token = create_access_token(
            user_data,
            refresh=True,
            expiry=timedelta(days=Config.REFESH_TOKEN_EXPIRE_DAYS),
        )
        return TokenResponseModel(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
        )
