"""HTTP-контроллеры товаров каталога."""

from typing import Annotated

from fastapi import APIRouter, Depends, Query, Response, status

from app.api.dependencies import get_app_id, get_product_service
from app.api.v1.dependencies import require_role
from app.core.roles import UserRole
from app.db.models import User
from app.schemas.product import ProductCreate, ProductResponse, ProductUpdate
from app.services.product import ProductService


router = APIRouter(tags=["products"])


@router.get("/", response_model=list[ProductResponse])
async def list_products(
    app_id: Annotated[str, Depends(get_app_id)],
    service: Annotated[ProductService, Depends(get_product_service)],
    category_id: Annotated[int | None, Query(ge=1)] = None,
    search: Annotated[str | None, Query(min_length=1, max_length=100)] = None,
    min_price: Annotated[float | None, Query(ge=0)] = None,
    max_price: Annotated[float | None, Query(ge=0)] = None,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> list[ProductResponse]:
    products = await service.list_for_tenant(
        app_id=app_id,
        category_id=category_id,
        search=search,
        min_price=min_price,
        max_price=max_price,
        limit=limit,
        offset=offset,
    )
    return [ProductResponse.model_validate(product) for product in products]


@router.get("/{product_id}", response_model=ProductResponse)
async def get_product(
    product_id: int,
    app_id: Annotated[str, Depends(get_app_id)],
    service: Annotated[ProductService, Depends(get_product_service)],
) -> ProductResponse:
    product = await service.get_by_id(product_id, app_id)
    return ProductResponse.model_validate(product)


@router.post(
    "/",
    response_model=ProductResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_product(
    data: ProductCreate,
    current_user: Annotated[
        User,
        Depends(require_role([UserRole.ADMIN.value])),
    ],
    app_id: Annotated[str, Depends(get_app_id)],
    service: Annotated[ProductService, Depends(get_product_service)],
) -> ProductResponse:
    product = await service.create(current_user.id, app_id, data)
    return ProductResponse.model_validate(product)


@router.put("/{product_id}", response_model=ProductResponse)
async def update_product(
    product_id: int,
    data: ProductUpdate,
    _: Annotated[
        User,
        Depends(require_role([UserRole.ADMIN.value])),
    ],
    app_id: Annotated[str, Depends(get_app_id)],
    service: Annotated[ProductService, Depends(get_product_service)],
) -> ProductResponse:
    product = await service.update(product_id, app_id, data)
    return ProductResponse.model_validate(product)


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(
    product_id: int,
    _: Annotated[
        User,
        Depends(require_role([UserRole.ADMIN.value])),
    ],
    app_id: Annotated[str, Depends(get_app_id)],
    service: Annotated[ProductService, Depends(get_product_service)],
) -> Response:
    await service.soft_delete(product_id, app_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
