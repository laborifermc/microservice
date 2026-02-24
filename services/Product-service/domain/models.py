from dataclasses import dataclass, field
from uuid import uuid4, UUID
from typing import Optional

@dataclass
class Product:
    name: str
    description: str
    category: str
    id: UUID = field(default_factory=uuid4)
    is_active: bool = True
