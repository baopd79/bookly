from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel.ext.asyncio.session import AsyncSession
from src.db.main import get_session
from src.auth.service import UserService, verify_password
from src.auth.schemas import (
    UserCreateModel,
    UserResponseModel,
    UserLoginModel,
    UserUpdateModel,
    TokenResponseModel,
)
from src.auth.utils import create_access_token, decode_token

import uuid

auth_router = APIRouter()
user_service = UserService()


# route đăng ký user mới
@auth_router.post(
    "/register", status_code=status.HTTP_201_CREATED, response_model=UserResponseModel
)  # response_model là kiểu dữ liệu trả về cho client sau khi đăng ký thành công, ở đây là UserResponseModel
async def register_user(
    user_data: UserCreateModel, session: AsyncSession = Depends(get_session)
):  # depend(get_session) để tự động tạo session và truyền vào hàm, không cần phải tạo thủ công
    user = await user_service.create_user(user_data, session)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Email {user_data.email} already exists",
        )
    return user


# router login
@auth_router.post("/login", response_model=TokenResponseModel)
async def login_user(
    login_data: UserLoginModel, session: AsyncSession = Depends(get_session)
):
    token_response = await user_service.login_user(
        login_data.email, login_data.password, session
    )
    if not token_response:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password"
        )
    return token_response

    # router lấy thông tin user theo uid


@auth_router.get("/{user_uid}", response_model=UserResponseModel)
async def get_user(user_uid: uuid.UUID, session: AsyncSession = Depends(get_session)):
    user = await user_service.get_user_by_uid(user_uid, session)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    return user


# router cap nhat thong tin user
@auth_router.patch("/{user_uid}", response_model=UserResponseModel)
async def update_user(
    user_uid: uuid.UUID,
    update_data: UserUpdateModel,
    session: AsyncSession = Depends(get_session),
):
    user = await user_service.update_user(user_uid, update_data, session)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    return user
