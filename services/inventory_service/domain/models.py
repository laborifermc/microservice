from pydantic import BaseModel
from uuid import UUID


class Inventory(BaseModel):
    product_id: UUID
    warehouse_id: UUID
    quantity: int = 0