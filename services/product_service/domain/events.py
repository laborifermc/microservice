from pydantic import BaseModel
from uuid import UUID
from datetime import datetime

class DomainEvent(BaseModel):
    occurred_at: datetime = datetime.now()

class ProductCreatedEvent(DomainEvent):
    product_id: UUID
    name: str

class ProductUpdatedEvent(DomainEvent):
    product_id: UUID
    name: str

class ProductDeletedEvent(DomainEvent):
    product_id: UUID