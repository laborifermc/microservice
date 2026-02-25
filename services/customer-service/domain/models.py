from pydantic import BaseModel, Field
from uuid import UUID, uuid4

class Customer(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    name: str
    email: str

    class Config:
        from_attributes = True