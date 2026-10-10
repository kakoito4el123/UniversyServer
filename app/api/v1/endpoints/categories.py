"""HTTP-контроллеры категорий каталога."""

from typing import Annotated

from fastapi import APIRouter, Depends, status

from app.api.dependencies import get_app_id, get_category_service
from app.api.v1.dependencies import require_role
from app.core.roles import UserRole
from app.db.models import Category, User
from app.schemas.category import CategoryCreate, CategoryResponse, CategoryUpdate
from app.services.category import CategoryService


router = APIRouter(tags=["categories"])


@router.get("/", response_model=list[CategoryResponse])
async def list_categories(
    app_id: Annotated[str, Depends(get_app_id)],
    service: Annotated[CategoryService, Depends(get_category_service)],
) -> list[CategoryResponse]:
    categories = await service.list_for_tenant(app_id)
    return [CategoryResponse.model_validate(category) for category in categories]


@router.post(
    "/",
    response_model=CategoryResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_category(
    data: CategoryCreate,
    current_user: Annotated[
        User,
        Depends(require_role([UserRole.ADMIN.value])),
    ],
    app_id: Annotated[str, Depends(get_app_id)],
    service: Annotated[CategoryService, Depends(get_category_service)],
) -> CategoryResponse:
    category: Category = await service.create(current_user.id, app_id, data)
    return CategoryResponse.model_validate(category)


@router.put("/{category_id}", response_model=CategoryResponse)
async def update_category(
    category_id: int,
    data: CategoryUpdate,
    _: Annotated[
        User,
        Depends(require_role([UserRole.ADMIN.value])),
    ],
    app_id: Annotated[str, Depends(get_app_id)],
    service: Annotated[CategoryService, Depends(get_category_service)],
) -> CategoryResponse:
    category = await service.update(category_id, app_id, data)
    return CategoryResponse.model_validate(category)
