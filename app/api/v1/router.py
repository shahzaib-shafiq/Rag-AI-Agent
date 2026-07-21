from fastapi import APIRouter

from app.api.v1.endpoints import health, products

router = APIRouter()

router.include_router(
    health.router,
    prefix="/health",
    tags=["Health"],
)

router.include_router(
    products.router,
    prefix="/products",
    tags=["Products"],
)