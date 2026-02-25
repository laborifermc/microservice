import zmq, json, threading, time
from fastapi import FastAPI
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from uuid import UUID
from sqlalchemy.exc import OperationalError

from infrastructure.db.models import Base
from infrastructure.db.uows import UnitOfWork
from infrastructure.db.repositories import InventoryRepository

app = FastAPI(title="Inventory Service")

DATABASE_URL = "postgresql://db_user:password@db:5432/inventory_db"
engine = create_engine(DATABASE_URL)
session_factory = sessionmaker(bind=engine)

DEFAULT_WAREHOUSE_ID = UUID("00000000-0000-0000-0000-000000000001")

def connect_db():
    retries = 10
    while retries > 0:
        try:
            Base.metadata.create_all(bind=engine)
            return True
        except OperationalError:
            retries -= 1
            time.sleep(2)
    return False

def start_zmq_subscriber():
    context = zmq.Context()
    subscriber = context.socket(zmq.SUB)
    
    # Connexion aux sources d'événements
    subscriber.connect("tcp://product-service:5555")
    subscriber.connect("tcp://order-service:5561")
    
    subscriber.setsockopt_string(zmq.SUBSCRIBE, "ProductCreatedEvent")
    subscriber.setsockopt_string(zmq.SUBSCRIBE, "OrderLineCreatedEvent")
    
    print("[Inventory-SUB] Listening on ports 5555 and 5561...")
    
    while True:
        try:
            raw_msg = subscriber.recv_string()
            topic, payload = raw_msg.split(' ', 1)
            data = json.loads(payload)
            
            # On récupère l'ID du produit de manière sécurisée (soit 'product_id', soit 'id')
            p_id = data.get('product_id') or data.get('id')
            if not p_id:
                print(f"[Inventory-SUB] Error: No ID found in payload {data}")
                continue

            with UnitOfWork(session_factory) as u:
                repo = InventoryRepository(u.session)
                
                if topic == "ProductCreatedEvent":
                    repo.initialize_stock(UUID(p_id), DEFAULT_WAREHOUSE_ID)
                    print(f"[Inventory] Successfully initialized product {p_id}")
                
                elif topic == "OrderLineCreatedEvent":
                    qty = int(data['quantity'])
                    repo.update_quantity(UUID(p_id), DEFAULT_WAREHOUSE_ID, -qty)
                    print(f"[Inventory] Stock REDUCED by {qty} for product {p_id}")
                    
        except Exception as e:
            print(f"[Inventory-SUB] Critical Error: {e}")

def start_zmq_responder():
    context = zmq.Context()
    responder = context.socket(zmq.REP)
    responder.bind("tcp://*:5557")
    print("[Inventory-REP] Ready on 5557")
    while True:
        request = responder.recv_json()
        product_id = request.get('product_id')
        with UnitOfWork(session_factory) as u:
            repo = InventoryRepository(u.session)
            total = repo.get_total_stock(UUID(product_id))
            responder.send_json({"product_id": str(product_id), "total_quantity": total})

if __name__ == "__main__":
    import uvicorn
    if connect_db():
        # ON LANCE LES THREADS ICI ET UNIQUEMENT ICI
        threading.Thread(target=start_zmq_subscriber, daemon=True).start()
        threading.Thread(target=start_zmq_responder, daemon=True).start()
        uvicorn.run(app, host="0.0.0.0", port=8000)