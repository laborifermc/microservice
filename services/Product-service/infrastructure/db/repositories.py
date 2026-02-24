# services/Product-service/infrastructure/db/repositories.py
from uuid import UUID
from .models import ProductTable
from domain.models import Product

class ProductRepository:
    def __init__(self, session):
        self.session = session

    def add(self, product: Product):
        db_prod = ProductTable(
            id=product.id,
            name=product.name,
            description=product.description,
            category=product.category,
            is_active=product.is_active
        )
        self.session.add(db_prod)

    def get_by_id(self, product_id: UUID):
        return self.session.query(ProductTable).filter_by(id=product_id).first()

    def update(self, product: Product):
        """Met à jour un produit existant en base"""
        db_prod = self.get_by_id(product.id)
        if db_prod:
            db_prod.name = product.name
            db_prod.description = product.description
            db_prod.category = product.category
            db_prod.is_active = product.is_active
        return db_prod

    def delete(self, product_id: UUID):
        """Supprime un produit de la base"""
        db_prod = self.get_by_id(product_id)
        if db_prod:
            self.session.delete(db_prod)
            return True
        return False