from infrastructure.messaging.zmq_client import ZmqClient

class ProductGatewayService:
    def __init__(self):
        # On définit les clients vers les différents services
        self.product_client = ZmqClient("product-service", 5554)
        self.pricing_client = ZmqClient("pricing-service", 5556)
        self.inventory_client = ZmqClient("inventory-service", 5557)

    def get_full_product(self, product_id: str):
        # 1. Demander les infos de base
        prod_info = self.product_client.request({"action": "get", "id": product_id})
        
        # 2. Demander le prix
        price_info = self.pricing_client.request({"product_id": product_id})
        
        # 3. Demander le stock
        stock_info = self.inventory_client.request({"product_id": product_id})

        # On fusionne tout pour le Front-end
        return {
            **prod_info,
            "price": price_info.get("price"),
            "stock": stock_info.get("total_quantity")
        }