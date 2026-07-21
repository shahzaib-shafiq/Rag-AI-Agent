from pydantic import BaseModel, ConfigDict, Field


class ProductBase(BaseModel):
    name: str = Field(
        min_length=2,
        max_length=100,
        examples=["Laptop"],
    )
    description: str | None = Field(
        default=None,
        max_length=500,
    )
    price: float = Field(
        gt=0,
        examples=[999.99],
    )
    quantity: int = Field(
        default=0,
        ge=0,
    )


class ProductCreate(ProductBase):
    pass


class ProductUpdate(BaseModel):
    name: str | None = Field(
        default=None,
        min_length=2,
        max_length=100,
    )
    description: str | None = Field(
        default=None,
        max_length=500,
    )
    price: float | None = Field(
        default=None,
        gt=0,
    )
    quantity: int | None = Field(
        default=None,
        ge=0,
    )


class ProductResponse(ProductBase):
    model_config = ConfigDict(from_attributes=True)

    id: int