from pydantic import BaseModel
from uuid import UUID

class Price(BaseModel):
    product_id: UUID
    value: float = 0.0

    class Config: from_attributes = True

