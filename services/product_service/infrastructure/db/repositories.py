from uuid import UUID as PyUUID
from .models import ProductTable
from domain.models import Product
from typing import List, Optional
from uuid import UUID    

class ProductRepository:
    def __init__(self, session):
        self.session = session

    def add(self, product: Product):
        db_prod = ProductTable(
            id=product.id, name=product.name, description=product.description,
            category=product.category, is_active=product.is_active
        )
        self.session.add(db_prod)


    def _get_db_obj(self, product_id: UUID) -> Optional[ProductTable]:
        return self.session.query(ProductTable).filter_by(id=product_id).first()
    
    def get_by_id(self, product_id: UUID) -> Optional[Product]: 
        db_prod = self._get_db_obj(product_id)
        return Product.model_validate(db_prod) if db_prod else None

    def list_all(self) -> List[Product]:
        db_products = self.session.query(ProductTable).all()
        return [Product.model_validate(p) for p in db_products]

    def update(self, product: Product):
        db_prod = self._get_db_obj(product.id)
        if db_prod:
            db_prod.name = product.name
            db_prod.description = product.description
            db_prod.category = product.category
            db_prod.is_active = product.is_active
        return db_prod

    def delete(self, product_id: UUID):
        
        db_prod = self._get_db_obj(product_id)
        if db_prod:
            self.session.delete(db_prod)
            return True
        return False