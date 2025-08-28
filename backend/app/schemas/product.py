from pydantic import BaseModel

class ProductOut(BaseModel):
    id: int
    name: str
    slug: str
    sku: str | None = None
    part_number: str | None = None
    excerpt: str | None = None
    description: str | None = None
    price: float
    compare_at_price: float | None = None
    stock_quantity: int
    stock_status: str
    brand_id: int | None = None

    class Config:
        from_attributes = True 