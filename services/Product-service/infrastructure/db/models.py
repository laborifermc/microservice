from sqlalchemy import Column, String, Boolean, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class ProductTable(Base):
    __tablename__ = 'products'
    id = Column(UUID(as_uuid=True), primary_key=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    category = Column(String(100))
    is_active = Column(Boolean, default=True)
