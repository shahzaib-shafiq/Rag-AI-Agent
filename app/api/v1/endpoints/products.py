from fastapi import APIRouter, HTTPException, status

from app.schemas.product import (
    ProductCreate,
    ProductResponse,
    ProductUpdate,
)

router = APIRouter()

products: list[ProductResponse] = []
next_product_id = 1


@router.get(
    "/",
    response_model=list[ProductResponse],
)
async def get_products() -> list[ProductResponse]:
    return products


@router.get(
    "/{product_id}",
    response_model=ProductResponse,
)
async def get_product(product_id: int) -> ProductResponse:
    for product in products:
        if product.id == product_id:
            return product

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Product not found",
    )


@router.post(
    "/",
    response_model=ProductResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_product(
    product_data: ProductCreate,
) -> ProductResponse:
    global next_product_id

    product = ProductResponse(
        id=next_product_id,
        **product_data.model_dump(),
    )

    products.append(product)
    next_product_id += 1

    return product


@router.patch(
    "/{product_id}",
    response_model=ProductResponse,
)
async def update_product(
    product_id: int,
    product_data: ProductUpdate,
) -> ProductResponse:
    for index, product in enumerate(products):
        if product.id != product_id:
            continue

        updated_data = product.model_dump()
        updated_data.update(
            product_data.model_dump(exclude_unset=True),
        )

        updated_product = ProductResponse(**updated_data)
        products[index] = updated_product

        return updated_product

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Product not found",
    )


@router.delete(
    "/{product_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_product(product_id: int) -> None:
    for index, product in enumerate(products):
        if product.id == product_id:
            products.pop(index)
            return

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Product not found",
    )