from datetime import datetime
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field


class UnitType(str, Enum):
    unit = "unit"
    kg = "kg"
    g = "g"
    l = "l"
    ml = "ml"


class PaymentMethod(str, Enum):
    cash = "cash"
    card = "card"
    transfer = "transfer"
    other = "other"


class InventoryTransactionType(str, Enum):
    entry = "entry"
    sale = "sale"
    adjustment = "adjustment"


class ProductContract(BaseModel):
    sku: str
    name: str
    barcode: Optional[str] = None
    unit_type: UnitType = UnitType.unit
    cost_price: float = Field(0, ge=0)
    sale_price: float = Field(0, ge=0)
    tax_rate: float = Field(0, ge=0)


class InventoryTransactionContract(BaseModel):
    product_id: int
    type: InventoryTransactionType
    quantity: int
    notes: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)


class SalesTicketLine(BaseModel):
    product_id: Optional[int] = None
    description: str
    quantity: float = Field(..., gt=0)
    unit_price: float = Field(..., ge=0)


class SalesTicketCreate(BaseModel):
    payment_method: PaymentMethod
    lines: List[SalesTicketLine] = Field(default_factory=list)
    notes: Optional[str] = None


class SalesTicket(BaseModel):
    id: int
    payment_method: PaymentMethod
    lines: List[SalesTicketLine]
    total_amount: float
    status: str = "draft"
    notes: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)


class OrderLine(BaseModel):
    product_id: Optional[int] = None
    description: str
    quantity: float = Field(..., gt=0)


class OrderCreate(BaseModel):
    customer_name: str
    customer_phone: Optional[str] = None
    channel: str = "web"
    lines: List[OrderLine] = Field(default_factory=list)
    notes: Optional[str] = None


class Order(BaseModel):
    id: int
    customer_name: str
    customer_phone: Optional[str] = None
    channel: str = "web"
    lines: List[OrderLine]
    status: str = "pending"
    notes: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)


class BootstrapContractsResponse(BaseModel):
    product_fields: List[str]
    mandatory_product_fields: List[str]
    order_statuses: List[str]
    ticket_statuses: List[str]
