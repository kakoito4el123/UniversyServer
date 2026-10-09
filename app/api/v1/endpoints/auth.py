"""HTTP endpoints for registration, login, token refresh, and logout."""

from typing import Annotated

from fastapi import APIRouter, Depends, Request, Response, status

from app.api.dependencies import get_auth_service
from app.core.exceptions import UnauthorizedError
from app.schemas.user import TokenResponse, UserCreate, UserResponse
from app.services.auth import AuthService


router = APIRouter(tags=["auth"])
REFRESH_COOKIE_NAME = "refresh_token"
REFRESH_COOKIE_MAX_AGE = 7 * 24 * 60 * 60


def set_refresh_cookie(response: Response, refresh_token: str) -> None:
    """Устанавливает защищенную HttpOnly cookie для refresh JWT."""
    response.set_cookie(
        key=REFRESH_COOKIE_NAME,
        value=refresh_token,
        httponly=True,
        secure=True,
        samesite="lax",
        max_age=REFRESH_COOKIE_MAX_AGE,
        path="/",
    )


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
async def register(
    data: UserCreate,
    service: Annotated[AuthService, Depends(get_auth_service)],
) -> UserResponse:
    user = await service.register(data.username, data.password)
    return UserResponse.model_validate(user)


@router.post("/login", response_model=TokenResponse)
async def login(
    data: UserCreate,
    response: Response,
    service: Annotated[AuthService, Depends(get_auth_service)],
) -> TokenResponse:
    access_token, refresh_token = await service.login(
        data.username,
        data.password,
    )
    set_refresh_cookie(response, refresh_token)
    return TokenResponse(access_token=access_token)


@router.post("/refresh", response_model=TokenResponse)
async def refresh(
    request: Request,
    response: Response,
    service: Annotated[AuthService, Depends(get_auth_service)],
) -> TokenResponse:
    refresh_token = request.cookies.get(REFRESH_COOKIE_NAME)
    if not refresh_token:
        raise UnauthorizedError("Refresh token отсутствует")

    access_token, rotated_refresh_token = await service.refresh_tokens(
        refresh_token
    )
    set_refresh_cookie(response, rotated_refresh_token)
    return TokenResponse(access_token=access_token)


@router.post("/logout")
async def logout(
    request: Request,
    response: Response,
    service: Annotated[AuthService, Depends(get_auth_service)],
) -> dict[str, str]:
    await service.revoke_refresh_token(
        request.cookies.get(REFRESH_COOKIE_NAME)
    )
    response.delete_cookie(key=REFRESH_COOKIE_NAME, path="/")
    return {"message": "Выход выполнен успешно"}
