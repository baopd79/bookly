from fastapi import HTTPException, status

# src/errors.py chứa các custom exception dùng chung trong toàn bộ project, giúp code gọn gàng hơn và dễ dàng quản lý lỗi hơn. Các exception này sẽ được raise trong service hoặc route khi có lỗi xảy ra, và FastAPI sẽ tự động chuyển chúng thành response với status code và message tương ứng.



class BooklyException(HTTPException):
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    detail = "Internal server error"

    def __init__(self, detail: str | None = None):
        super().__init__(
            status_code=self.status_code,
            detail=detail or self.detail,
        )

#NotFoundException là class cha 

class NotFoundException(BooklyException):
    status_code = status.HTTP_404_NOT_FOUND
    detail = "Resource not found"

class BookNotFoundException(NotFoundException):
    detail = "Book not found"


class UserNotFoundException(NotFoundException):
    detail = "User not found"


class ReviewNotFoundException(NotFoundException):
    detail = "Review not found"


class AuthException(BooklyException):
    status_code = status.HTTP_401_UNAUTHORIZED
    detail = "Authentication required"


class InvalidCredentialsException(AuthException):
    detail = "Invalid email or password"


class InvalidTokenException(AuthException):
    detail = "Invalid token"


class ForbiddenException(BooklyException):
    status_code = status.HTTP_403_FORBIDDEN
    detail = "Forbidden"


class InsufficientPermissionsException(ForbiddenException):
    detail = "Insufficient permissions"


class UnauthorizedReviewAccessException(ForbiddenException):
    def __init__(self, action: str = "access"):
        super().__init__(detail=f"Not authorized to {action} this review")


class EmailAlreadyExistsException(BooklyException):
    status_code = status.HTTP_409_CONFLICT
    detail = "Email already exists"

    def __init__(self, email: str):
        super().__init__(detail=f"Email {email} already exists")
