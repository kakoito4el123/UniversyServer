"""HTTP-контроллеры корзины покупателя."""

from typing import Annotated

from fastapi import APIRouter, Depends, Response, status

from app.api.dependencies import get_app_id, get_cart_service, get_current_user
from app.db.models import User
from app.schemas.cart import (
    CartItemCreate,
    CartItemResponse,
    CartItemUpdate,
    CartSummaryResponse,
)
from app.services.cart import CartService


router = APIRouter(tags=["cart"])


@router.get("/", response_model=CartSummaryResponse)
async def get_cart(
    current_user: Annotated[User, Depends(get_current_user)],
    app_id: Annotated[str, Depends(get_app_id)],
    service: Annotated[CartService, Depends(get_cart_service)],
) -> CartSummaryResponse:
    return await service.get_user_cart(current_user.id, app_id)


@router.post(
    "/items",
    response_model=CartItemResponse,
    status_code=status.HTTP_201_CREATED,
)
async def add_cart_item(
    data: CartItemCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    app_id: Annotated[str, Depends(get_app_id)],
    service: Annotated[CartService, Depends(get_cart_service)],
) -> CartItemResponse:
    item = await service.add_to_cart(current_user.id, app_id, data)
    return CartItemResponse.model_validate(item)


@router.patch("/items/{item_id}", response_model=CartItemResponse)
async def update_cart_item(
    item_id: int,
    data: CartItemUpdate,
    current_user: Annotated[User, Depends(get_current_user)],
    app_id: Annotated[str, Depends(get_app_id)],
    service: Annotated[CartService, Depends(get_cart_service)],
) -> CartItemResponse:
    item = await service.update_item(item_id, current_user.id, app_id, data)
    return CartItemResponse.model_validate(item)


@router.delete("/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_cart_item(
    item_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    app_id: Annotated[str, Depends(get_app_id)],
    service: Annotated[CartService, Depends(get_cart_service)],
) -> Response:
    await service.remove_item(item_id, current_user.id, app_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.delete("/", status_code=status.HTTP_204_NO_CONTENT)
async def clear_cart(
    current_user: Annotated[User, Depends(get_current_user)],
    app_id: Annotated[str, Depends(get_app_id)],
    service: Annotated[CartService, Depends(get_cart_service)],
) -> Response:
    await service.clear_cart(current_user.id, app_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
