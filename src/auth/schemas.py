# # UserCreateModel   → client gửi lên khi đăng ký
#                     có password plain text
#                     KHÔNG có uid, created_at

# UserResponseModel → server trả về sau khi tạo
#                     KHÔNG có password
#                     CÓ uid, created_at

# UserLoginModel    → client gửi lên khi đăng nhập
#                     chỉ cần email + password

from pydantic import BaseModel, EmailStr, field_validator
import uuid
from datetime import datetime, date


class UserCreateModel(BaseModel):
    username: str
    email: EmailStr
    password: str
    first_name: str
    last_name: str
    birthday: date | None = None

    @field_validator("password")
    @classmethod
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError("Password phai co it nhat 8 ki tu")

        if not any(c.isupper() for c in v):
            raise ValueError("password phai co it nhat 1 chu in hoa")
        if not any(c.isdigit() for c in v):
            raise ValueError("Password phai co it nhat 1 so")
        return v

    @field_validator("username")
    @classmethod
    def validate_username(cls, v):
        if len(v) < 3:
            raise ValueError("Username phai co it nhat 3 ki tu")
        if not v.isalnum():
            raise ValueError("Username chi duoc chua chu va so")
        return v.lower()


class UserResponseModel(BaseModel):
    uid: uuid.UUID
    username: str
    email: str
    first_name: str
    last_name: str
    birthday: date | None = None
    role: str
    is_verified: bool
    created_at: datetime
    updated_at: datetime


class UserLoginModel(BaseModel):
    email: EmailStr
    password: str


class UserUpdateModel(BaseModel):
    username: str | None = None
    first_name: str | None = None
    last_name: str | None = None
    birthday: date | None = None


class TokenResponseModel(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshTokenModel(BaseModel):
    refresh_token: str
