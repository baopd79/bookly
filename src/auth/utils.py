# file ultis.py chứa các hàm tiện ích dùng chung trong auth, có thể dùng chung cho cả user và token
# có nhiệm vụ chính là tạo hash password và verify password, tạo access token và refresh token


from jose import jwt, JWTError
from passlib.context import CryptContext
from datetime import datetime, timedelta
from src.config import Config
import uuid


# tạo access token
# Tạo JWT token — access hoặc refresh
# refresh=True → refresh token, thời gian expire dài hơn
# nhiệm vụ của hàm create_access_token là tạo access token hoặc refresh token dựa trên user_data và expiry time, nếu refresh=True thì sẽ tạo refresh token với thời gian expire dài hơn, nếu refresh=False thì sẽ tạo access token với thời gian expire ngắn hơn


def create_access_token(
    user_data: dict, expiry: timedelta | None = None, refresh: bool = False
) -> str:
    payload = {}
    payload["user"] = user_data
    payload["exp"] = datetime.now() + (
        expiry
        if expiry is not None
        else timedelta(minutes=Config.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    payload["refresh"] = refresh
    token = jwt.encode(payload, Config.SECRET_KEY, algorithm=Config.ALGORITHM)
    return token


# verify token and decode token
# nhiệm vụ của hàm decode_token là decode token và trả về payload nếu token hợp lệ, nếu token không hợp lệ thì trả về None hoặc raise exception tùy theo nhu cầu
def decode_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, Config.SECRET_KEY, algorithms=[Config.ALGORITHM])
        return payload
    except JWTError:
        return None
