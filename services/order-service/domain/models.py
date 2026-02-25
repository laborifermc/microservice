from pydantic import BaseModel, Field
from uuid import UUID, uuid4
from typing import List

class OrderLine(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    product_id: UUID
    quantity: int

class Order(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    customer_id: UUID
    total_amount: float
    lines: List[OrderLine] = []

    class Config:
        from_attributes = True