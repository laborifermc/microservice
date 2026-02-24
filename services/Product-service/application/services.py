# services/Product-service/application/services.py
from uuid import UUID
import json
from domain.models import Product
from infrastructure.db.repositories import ProductRepository

class ProductApplicationService:
    def __init__(self, uow, mq_channel):
        self.uow = uow
        self.mq_channel = mq_channel

    # ... (create_product déjà vu) ...

    def update_product(self, product_id: UUID, dto):
        with self.uow as uow:
            repo = ProductRepository(uow.session)
            db_prod = repo.get_by_id(product_id)
            
            if not db_prod:
                return None
            
            # On utilise le modèle de domaine Pydantic pour valider la logique
            product_domain = Product.model_validate(db_prod)
            product_domain.name = dto.name
            product_domain.description = dto.description
            product_domain.category = dto.category
            
            repo.update(product_domain)
            
            # Optionnel : Notifier d'un changement de nom si besoin
            self._notify("product.updated", {"id": str(product_id), "name": dto.name})
            
            return product_domain

    def delete_product(self, product_id: UUID):
        with self.uow as uow:
            repo = ProductRepository(uow.session)
            success = repo.delete(product_id)
            
            if success:
                self._notify("product.deleted", {"id": str(product_id)})
                
            return success

    def _notify(self, routing_key, data):
        """Méthode helper pour envoyer des messages RabbitMQ"""
        self.mq_channel.basic_publish(
            exchange='product_events',
            routing_key=routing_key,
            body=json.dumps(data)
        )