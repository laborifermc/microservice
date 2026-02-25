from uuid import UUID
from typing import Optional, List
from .models import CustomerTable
from domain.models import Customer

class CustomerRepository:
    def __init__(self, session):
        self.session = session

    def _get_db_obj(self, customer_id: UUID):
        return self.session.query(CustomerTable).filter_by(id=customer_id).first()

    def add(self, customer: Customer):
        db_cust = CustomerTable(id=customer.id, name=customer.name, email=customer.email)
        self.session.add(db_cust)

    def get_by_id(self, customer_id: UUID) -> Optional[Customer]:
        db_cust = self._get_db_obj(customer_id)
        return Customer.model_validate(db_cust) if db_cust else None