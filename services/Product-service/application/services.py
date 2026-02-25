from uuid import UUID
import json
from domain.models import Product
from infrastructure.db.repositories import ProductRepository
from application.dtos import ProductCreateDTO

class ProductApplicationService:
    def __init__(self, uow, mq_channel):
        self.uow = uow
        self.mq_channel = mq_channel

    def create_product(self, dto: ProductCreateDTO):
        new_product = Product(name=dto.name, description=dto.description, category=dto.category)
        with self.uow as uow:
            repo = ProductRepository(uow.session)
            repo.add(new_product)
        self._notify("product.created", {"id": str(new_product.id), "action": "create"})
        return new_product

    def get_all_products(self):
        with self.uow as uow:
            repo = ProductRepository(uow.session)
            return [Product.model_validate(p) for p in repo.list_all()]

    def get_product(self, product_id: UUID):
        with self.uow as uow:
            repo = ProductRepository(uow.session)
            db_prod = repo.get_by_id(product_id)
            return Product.model_validate(db_prod) if db_prod else None

    def update_product(self, product_id: UUID, dto: ProductCreateDTO):
        with self.uow as uow:
            repo = ProductRepository(uow.session)
            
            product_domain = repo.get_by_id(product_id)
            
            if not product_domain:
                return None
            
            
            product_domain.name = dto.name
            product_domain.description = dto.description
            product_domain.category = dto.category
            

            repo.update(product_domain)
            
           
            self._notify("product.updated", {"id": str(product_id), "name": dto.name})
            
            return product_domain

    def delete_product(self, product_id: UUID):
        with self.uow as uow:
            repo = ProductRepository(uow.session)
            if repo.delete(product_id):
                self._notify("product.deleted", {"id": str(product_id)})
                return True
        return False

    def _notify(self, routing_key, data):
        if self.mq_channel:
            self.mq_channel.basic_publish(exchange='product_events', routing_key=routing_key, body=json.dumps(data))