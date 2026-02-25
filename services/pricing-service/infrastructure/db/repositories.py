from uuid import UUID
from typing import Optional
from sqlalchemy.orm import Session
from .models import PriceTable
from domain.models import Price

class PriceRepository:
    def __init__(self, session: Session):
        self.session = session

    def _get_db_obj(self, product_id: UUID) -> Optional[PriceTable]:
        return self.session.query(PriceTable).filter_by(product_id=product_id).first()

    def get_by_product_id(self, product_id: UUID) -> Optional[Price]:
        db_price = self._get_db_obj(product_id)
        return Price.model_validate(db_price) if db_price else None

    def add_default_price(self, product_id: UUID):
        """Initialise un prix à 0.0 si le produit n'existe pas encore"""
        if not self._get_db_obj(product_id):
            db_price = PriceTable(product_id=product_id, value=0.0)
            self.session.add(db_price)

    def update_price(self, product_id: UUID, new_value: float):
        db_price = self._get_db_obj(product_id)
        if db_price:
            db_price.value = new_value
        return db_price