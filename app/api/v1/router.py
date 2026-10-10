"""Корневой router версии API v1."""

from fastapi import APIRouter

from app.api.v1.endpoints.admin import router as admin_router
from app.api.v1.endpoints.app_settings import router as app_settings_router
from app.api.v1.endpoints.auth import router as auth_router
from app.api.v1.endpoints.cart import router as cart_router
from app.api.v1.endpoints.categories import router as categories_router
from app.api.v1.endpoints.notes import router as notes_router
from app.api.v1.endpoints.orders import router as orders_router
from app.api.v1.endpoints.products import router as products_router
from app.api.v1.users import router as users_router


router = APIRouter()
router.include_router(auth_router, prefix="/auth")
router.include_router(app_settings_router, prefix="/apps/settings")
router.include_router(cart_router, prefix="/cart")
router.include_router(categories_router, prefix="/categories")
router.include_router(notes_router, prefix="/notes")
router.include_router(orders_router, prefix="/orders")
router.include_router(products_router, prefix="/products")
router.include_router(users_router, prefix="/users")
router.include_router(admin_router, prefix="/admin")
