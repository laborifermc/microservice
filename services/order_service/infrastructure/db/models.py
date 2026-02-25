from sqlalchemy import Column, Float, Integer, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class OrderTable(Base):
    __tablename__ = 'orders'
    id = Column(UUID(as_uuid=True), primary_key=True)
    customer_id = Column(UUID(as_uuid=True), nullable=False)
    total_amount = Column(Float)
    lines = relationship("OrderLineTable", back_populates="order")

class OrderLineTable(Base):
    __tablename__ = 'order_lines'
    id = Column(UUID(as_uuid=True), primary_key=True)
    order_id = Column(UUID(as_uuid=True), ForeignKey('orders.id'))
    product_id = Column(UUID(as_uuid=True), nullable=False)
    quantity = Column(Integer)
    order = relationship("OrderTable", back_populates="lines")