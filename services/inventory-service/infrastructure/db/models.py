from sqlalchemy import Column, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base

# Définition de la Base pour l'ORM
Base = declarative_base()

class InventoryTable(Base):
    __tablename__ = 'inventories'
    
    product_id = Column(UUID(as_uuid=True), primary_key=True)
    warehouse_id = Column(UUID(as_uuid=True), primary_key=True)
    
    # La quantité en stock
    quantity = Column(Integer, default=0)