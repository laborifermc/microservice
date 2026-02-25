from sqlalchemy import Column, Float
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class PriceTable(Base):
    __tablename__ = 'prices'
    
    # L'ID du produit sert de clé primaire ici. 
    # Un produit = un prix dans ce service.
    product_id = Column(UUID(as_uuid=True), primary_key=True)
    value = Column(Float, default=0.0)