from fastapi import APIRouter, HTTPException
from uuid import UUID
from typing import List
from infrastructure.messaging.zmq_client import ZmqClient

router = APIRouter()

# Initialisation des clients ZMQ vers les services (flux bleu sur ton schéma)
product_client = ZmqClient("product-service", 5554)
pricing_client = ZmqClient("pricing-service", 5556)
inventory_client = ZmqClient("inventory-service", 5557)
customer_client = ZmqClient("customer-service", 5558)
order_client = ZmqClient("order-service", 5560)

# --- ROUTES PRODUCT ---

@router.post("/product", status_code=201)
def create_product(data: dict):
    # Demande de création au Product Service
    return product_client.request({"action": "create", "data": data})

@router.get("/product/{pk}")
def get_full_product(pk: UUID):
    """
    AGRÉGATION : Cette route interroge les 3 services pour 
    renvoyer un objet complet au Front-end.
    """
    # 1. Infos de base (Nom, Desc, etc.)
    product = product_client.request({"action": "get_one", "id": str(pk)})
    if "error" in product:
        raise HTTPException(status_code=404, detail="Product not found")

    # 2. Prix depuis Pricing Service
    price_data = pricing_client.request({"product_id": str(pk)})

    # 3. Stock depuis Inventory Service
    inventory_data = inventory_client.request({"product_id": str(pk)})

    # Fusion des données
    return {
        **product,
        "price": price_data.get("price", 0.0),
        "stock": inventory_data.get("total_quantity", 0)
    }


@router.get("/products") 
def list_products():
    return product_client.request({"action": "list_all"})

@router.put("/product/{pk}") # Correction du nom du paramètre {pk}
def update_product(pk: UUID, data: dict):
    return product_client.request({"action": "update", "id": str(pk), "data": data})

@router.delete("/product/{pk}") # AJOUTE CETTE ROUTE
def delete_product(pk: UUID):
    return product_client.request({"action": "delete", "id": str(pk)})


# --- ROUTES INVENTORY ---

@router.get("/inventory/{product_pk}")
def get_inventory(product_pk: UUID):
    return inventory_client.request({"product_id": str(product_pk)})



@router.patch("/inventory/{warehouse_pk}/{product_pk}")
def update_stock(warehouse_pk: UUID, product_pk: UUID, quantity: int):
    return inventory_client.request({
        "action": "update_stock",
        "warehouse_id": str(warehouse_pk),
        "product_id": str(product_pk),
        "quantity": quantity
    })

# --- ROUTES PRICING ---

@router.get("/pricing/{product_pk}")
def get_pricing(product_pk: UUID):
    return pricing_client.request({"product_id": str(product_pk)})


# --- ROUTES ORDER ---
@router.post("/order")
def create_order(data: dict):
    """
    Format data attendu : 
    {
      "customer_id": "uuid...",
      "total_amount": 150.0,
      "lines": [{"product_id": "uuid...", "quantity": 2}]
    }
    """
    # 1. Optionnel : Vérifier si le client existe via customer_client.request(...)
    # 2. Envoyer la commande
    return order_client.request({"action": "create_order", "data": data})

# --- ROUTES CUSTOMER ---
@router.post("/customer")
def create_customer(data: dict):
    return customer_client.request({"action": "create", "data": data})
