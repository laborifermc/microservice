from .models import OrderTable, OrderLineTable
from domain.models import Order

class OrderRepository:
    def __init__(self, session):
        self.session = session

    def create_order(self, order: Order):
        db_order = OrderTable(id=order.id, customer_id=order.customer_id, total_amount=order.total_amount)
        self.session.add(db_order)
        
        for line in order.lines:
            db_line = OrderLineTable(id=line.id, order_id=order.id, product_id=line.product_id, quantity=line.quantity)
            self.session.add(db_line)
        return order