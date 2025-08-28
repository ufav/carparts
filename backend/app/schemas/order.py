from pydantic import BaseModel
from typing import List
from app.schemas.product import ProductOut


class CheckoutItemOptionData(BaseModel):
    name: str
    value: str


class CheckoutItemData(BaseModel):
    productId: int
    options: List[CheckoutItemOptionData]
    quantity: int


class AddressData(BaseModel):
    firstName: str
    lastName: str
    email: str | None = None
    phone: str
    company: str | None = None
    address1: str
    address2: str | None = None
    city: str
    state: str | None = None
    country: str | None = None
    postcode: str | None = None


class CheckoutIn(BaseModel):
    payment: str
    items: List[CheckoutItemData]
    billingAddress: AddressData
    shippingAddress: AddressData
    comment: str | None = None


class OrderItemOption(BaseModel):
    name: str
    value: str


class OrderItem(BaseModel):
    product: ProductOut
    options: List[OrderItemOption]
    price: float
    quantity: int
    total: float


class OrderTotal(BaseModel):
    title: str
    price: float


class OrderOut(BaseModel):
    id: int
    token: str
    number: str
    createdAt: str
    payment: str
    status: str
    items: List[OrderItem]
    quantity: int
    subtotal: float
    totals: List[OrderTotal]
    total: float
    shippingAddress: AddressData
    billingAddress: AddressData


