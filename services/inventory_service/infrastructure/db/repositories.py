from uuid import UUID
from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import func
from .models import InventoryTable
from domain.models import Inventory

class InventoryRepository:
    def __init__(self, session: Session):
        self.session = session

    def _get_db_obj(self, product_id: UUID, warehouse_id: UUID) -> Optional[InventoryTable]:
        return self.session.query(InventoryTable).filter_by(
            product_id=product_id, 
            warehouse_id=warehouse_id
        ).first()

    def initialize_stock(self, product_id: UUID, warehouse_id: UUID):
        """Crée une entrée de stock à 0 pour un nouveau produit"""
        if not self._get_db_obj(product_id, warehouse_id):
            db_inventory = InventoryTable(
                product_id=product_id, 
                warehouse_id=warehouse_id, 
                quantity=0
            )
            self.session.add(db_inventory)

    def get_total_stock(self, product_id: UUID) -> int:
        """Calcule la somme de tous les stocks pour un produit (tous entrepôts confondus)"""
        total = self.session.query(func.sum(InventoryTable.quantity))\
            .filter(InventoryTable.product_id == product_id).scalar()
        return total if total is not None else 0

    def update_quantity(self, product_id: UUID, warehouse_id: UUID, change_qty: int):
        db_inv = self._get_db_obj(product_id, warehouse_id)
        
        if not db_inv:
            # Si la ligne n'existe pas, on la crée avec la quantité
            db_inv = InventoryTable(
                product_id=product_id, 
                warehouse_id=warehouse_id, 
                quantity=change_qty
            )
            self.session.add(db_inv)
        else:
            # Si elle existe, on ajoute (ou soustrait)
            db_inv.quantity += change_qty
            
        print(f"DEBUG DB: Product {product_id} quantity is now {db_inv.quantity}")
        return db_inv