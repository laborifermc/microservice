from uuid import UUID
import json
from domain.models import Product
from infrastructure.db.repositories import ProductRepository
from application.dtos import ProductCreateDTO
from domain.events import ProductCreatedEvent, ProductUpdatedEvent, ProductDeletedEvent

class ProductApplicationService:
    def __init__(self, uow, event_dispatcher):
        self.uow = uow
        self.event_dispatcher = event_dispatcher

    def create_product(self, dto: ProductCreateDTO):
        new_product = Product(name=dto.name, description=dto.description, category=dto.category)
        with self.uow as uow:
            repo = ProductRepository(uow.session)
            repo.add(new_product)

        event = ProductCreatedEvent(product_id=new_product.id, name=new_product.name)
        self.event_dispatcher.handle_event(event)
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
            
           
            event =  ProductUpdatedEvent(product_id=product_id)
            self.event_dispatcher.handle_event(event)
            
            return product_domain

    def delete_product(self, product_id: UUID):
        with self.uow as uow:
            repo = ProductRepository(uow.session)
            if repo.delete(product_id):
                event = ProductDeletedEvent(product_id=product_id)
                self.event_dispatcher.handle_event(event)
                return True
        return False
