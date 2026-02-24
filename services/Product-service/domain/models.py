from dataclasses import dataclass, field
from uuid import uuid4, UUID
from typing import Optional

@dataclass
class Product:
    name: str
    description: str
    price: float
    stock_quantity: int
    stock: str  
    category: str
    id: UUID = field(default_factory=uuid4)
    is_active: bool = True

    def update_price(self, new_price: float):
        if new_price < 0:
            raise ValueError("Le prix ne peut pas être négatif")
        self.price = new_price

    def update_stock(self, quantity: int):
        if quantity < 0:
            raise ValueError("Le stock ne peut pas être inférieur à zéro")
        self.stock_quantity = quantity