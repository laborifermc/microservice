import zmq
import json
import time
from uuid import UUID
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from infrastructure.db.models import Base
from infrastructure.db.uows import UnitOfWork
from infrastructure.messaging.zmq_publisher import ZmqPublisher
from application.services import ProductApplicationService
from application.dtos import ProductCreateDTO
from sqlalchemy.exc import OperationalError

# --- CONFIGURATION DB ---
DATABASE_URL = "postgresql://db_user:password@db:5432/product_db"
engine = create_engine(DATABASE_URL)


def bootstrap_databases():
    """
    Se connecte à la DB 'postgres' (par défaut) pour créer les autres bases.
    """
    # URL de connexion à la base système
    admin_url = "postgresql://db_user:password@db:5432/postgres"
    engine = create_engine(admin_url)
    
    # Liste des bases à créer
    databases = ["product_db", "pricing_db", "inventory_db", "customer_db", "order_db"]
    
    # On tente de se connecter jusqu'à ce que Postgres soit prêt
    retries = 10
    conn = None
    while retries > 0:
        try:
            # Important : on doit être en mode AUTOCOMMIT pour créer une base
            conn = engine.connect().execution_options(isolation_level="AUTOCOMMIT")
            print("[Bootstrap] Connected to PostgreSQL system.")
            break
        except OperationalError:
            retries -= 1
            print(f"[Bootstrap] Waiting for Postgres... ({retries} left)")
            time.sleep(2)
    
    if not conn:
        return False

    for db in databases:
        try:
            conn.execute(text(f"CREATE DATABASE {db}"))
            print(f"[Bootstrap] Database '{db}' created successfully.")
        except ProgrammingError:
            # Cette erreur arrive si la base existe déjà, on l'ignore proprement
            print(f"[Bootstrap] Database '{db}' already exists, skipping.")
        except Exception as e:
            print(f"[Bootstrap] Error creating '{db}': {e}")
            
    conn.close()
    return True

def connect_db():
    retries = 10
    while retries > 0:
        try:
            print(f"Attempting to connect to DB... ({retries} retries left)")
            Base.metadata.create_all(bind=engine)
            print("Successfully connected to DB and created tables!")
            return True
        except OperationalError:
            retries -= 1
            time.sleep(2)  # Attendre 2 secondes avant de réessayer
    return False

if not connect_db():
    print("Could not connect to DB. Exiting.")
    exit(1)


Base.metadata.create_all(bind=engine)
session_factory = sessionmaker(bind=engine)

# --- SERVICES ---
# Publisher pour les événements (ProductCreatedEvent...) vers Pricing/Inventory
zmq_publisher = ZmqPublisher(port=5555)

def get_product_service():
    uow = UnitOfWork(session_factory)
    return ProductApplicationService(uow, event_dispatcher=zmq_publisher)

# --- SERVEUR ZMQ REP (Répondeur pour la Gateway) ---
def start_responder():
    context = zmq.Context()
    socket = context.socket(zmq.REP)
    socket.bind("tcp://*:5554")
    
    service = get_product_service()
    print("[Product-Service] ZMQ Responder ready on port 5554 (Waiting for Gateway...)")
    
    if connect_db():
        while True:
            # Attente d'une requête de la Gateway
            request = socket.recv_json()
            action = request.get("action")
            
            try:
                if action == "create":
                    dto = ProductCreateDTO(**request["data"])
                    product = service.create_product(dto)
                    socket.send_json(json.loads(product.model_dump_json()))

                elif action == "get_one":
                    product_id = UUID(request["id"])
                    product = service.get_product(product_id)
                    if product:
                        socket.send_json(json.loads(product.model_dump_json()))
                    else:
                        socket.send_json({"error": "not_found"})

                elif action == "update":
                    product_id = UUID(request["id"])
                    dto = ProductCreateDTO(**request["data"])
                    product = service.update_product(product_id, dto)
                    socket.send_json(product.model_dump() if product else {"error": "not_found"})

                elif action == "delete":
                    product_id = UUID(request["id"])
                    success = service.delete_product(product_id)
                    socket.send_json({"status": "success" if success else "failed"})

                else:
                    socket.send_json({"error": "Unknown action"})

            except Exception as e:
                print(f"Error processing request: {e}")
                socket.send_json({"error": str(e)})

if __name__ == "__main__":
    if bootstrap_databases():
        if connect_db():
            start_responder()