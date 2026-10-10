"""HTTP-контроллеры заказов."""

from typing import Annotated

from fastapi import APIRouter, Depends, Query, status

from app.api.dependencies import (
    get_app_id,
    get_current_user,
    get_order_service,
)
from app.api.v1.dependencies import require_role
from app.core.roles import UserRole
from app.db.models import User
from app.schemas.order import OrderCreate, OrderResponse, OrderStatusUpdate
from app.services.order import OrderService


router = APIRouter(tags=["orders"])


@router.post("/", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
async def create_order(
    data: OrderCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    app_id: Annotated[str, Depends(get_app_id)],
    service: Annotated[OrderService, Depends(get_order_service)],
) -> OrderResponse:
    return await service.create_order_from_cart(current_user.id, app_id, data)


@router.get("/", response_model=list[OrderResponse])
async def list_my_orders(
    current_user: Annotated[User, Depends(get_current_user)],
    app_id: Annotated[str, Depends(get_app_id)],
    service: Annotated[OrderService, Depends(get_order_service)],
) -> list[OrderResponse]:
    return await service.list_my_orders(current_user.id, app_id)


@router.get("/admin/all", response_model=list[OrderResponse])
async def list_all_orders(
    _: Annotated[
        User,
        Depends(require_role([UserRole.ADMIN.value])),
    ],
    app_id: Annotated[str, Depends(get_app_id)],
    service: Annotated[OrderService, Depends(get_order_service)],
    order_status: Annotated[str | None, Query(alias="status")] = None,
) -> list[OrderResponse]:
    return await service.list_all_orders(app_id, order_status)


@router.patch("/{order_id}/status", response_model=OrderResponse)
async def update_order_status(
    order_id: int,
    data: OrderStatusUpdate,
    _: Annotated[
        User,
        Depends(require_role([UserRole.ADMIN.value])),
    ],
    app_id: Annotated[str, Depends(get_app_id)],
    service: Annotated[OrderService, Depends(get_order_service)],
) -> OrderResponse:
    return await service.update_status(order_id, app_id, data.status)


@router.post("/{order_id}/pay", response_model=OrderResponse)
async def pay_order(
    order_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    app_id: Annotated[str, Depends(get_app_id)],
    service: Annotated[OrderService, Depends(get_order_service)],
) -> OrderResponse:
    return await service.pay_order_with_balance(order_id, app_id, current_user)


@router.get("/{order_id}", response_model=OrderResponse)
async def get_order(
    order_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    app_id: Annotated[str, Depends(get_app_id)],
    service: Annotated[OrderService, Depends(get_order_service)],
) -> OrderResponse:
    return await service.get_order(order_id, app_id, current_user)
