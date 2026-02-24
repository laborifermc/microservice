from pydantic import BaseModel, Field
from uuid import UUID, uuid4

class Product(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    name: str
    description: str
    category: str
    is_active: bool = True