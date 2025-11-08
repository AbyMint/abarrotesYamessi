from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class ProductBase(BaseModel):
    sku: str
    name: str
    category: Optional[str] = None
    subcategory: Optional[str] = None
    cost_price: Optional[float] = 0.0
    sale_price: Optional[float] = 0.0


class ProductCreate(ProductBase):
    pass


class Product(ProductBase):
    id: int
    stock: int

    class Config:
        orm_mode = True


class SupplierBase(BaseModel):
    name: str
    contact: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None


class SupplierCreate(SupplierBase):
    pass


class Supplier(SupplierBase):
    id: int

    class Config:
        orm_mode = True


class MovementBase(BaseModel):
    product_id: int
    type: str
    quantity: int
    supplier_id: Optional[int] = None
    notes: Optional[str] = None


class MovementCreate(MovementBase):
    pass


class Movement(MovementBase):
    id: int
    date: datetime

    class Config:
        orm_mode = True
