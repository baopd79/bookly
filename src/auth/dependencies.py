# file dependencies.py chứa các dependency dùng chung trong auth, có thể dùng chung cho cả user và token
# có nhiệm vụ chính là tạo session và get current user
# get_current_user sẽ được dùng trong các route cần xác thực user, nó sẽ decode token từ header, lấy uid từ payload, tìm user theo uid và trả về user nếu token hợp lệ, nếu token không hợp lệ hoặc user không tồn tại thì trả về None hoặc raise exception tùy theo nhu cầu
# get_session sẽ được dùng trong các route cần truy cập database, nó sẽ tạo session mới và trả về session đó, sau khi request kết thúc thì session sẽ tự động đóng lại
# các route trong routes.py sẽ dùng Depends để gọi các dependency này, ví dụ: session: AsyncSession = Depends(get_session) hoặc current_user: User = Depends(get_current_user) để tự động tạo session hoặc lấy current user mà không cần phải làm thủ công trong từng route

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlmodel.ext.asyncio.session import AsyncSession
from src.db.main import get_session
from src.auth.utils import decode_token
from src.auth.service import UserService

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

user_service = UserService()


async def get_current_user(
    token: str = Depends(oauth2_scheme), session: AsyncSession = Depends(get_session)
):
    # decode token để lấy payload
    payload = decode_token(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
        )
    # check nếu token là refresh token thì không cho truy cập
    if payload.get("refresh", False):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
        )

    # get user uid từ payload
    user_uid = payload["user"]["uid"]
    # tìm user trong DB
    user = await user_service.get_user_by_uid(user_uid, session)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found"
        )
    return user
