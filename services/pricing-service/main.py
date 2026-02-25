import zmq
import json
import threading
from fastapi import FastAPI
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from uuid import UUID
import time
from sqlalchemy.exc import OperationalError

from infrastructure.db.models import Base, PriceTable
from infrastructure.db.uows import UnitOfWork
from infrastructure.db.repositories import PriceRepository

app = FastAPI(title="Pricing Service")

# DB Setup (Base unique, DB différente)
DATABASE_URL = "postgresql://db_user:password@db:5432/pricing_db"
engine = create_engine(DATABASE_URL)

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

# --- LOGIQUE ZMQ SUB (Écoute la création de produit) ---
def start_zmq_subscriber():
    context = zmq.Context()
    subscriber = context.socket(zmq.SUB)
    # Se connecte au product-service sur son port de publication
    subscriber.connect("tcp://product-service:5555")
    subscriber.setsockopt_string(zmq.SUBSCRIBE, "ProductCreatedEvent")
    
    print("[Pricing] ZMQ Subscriber started, listening for ProductCreatedEvent...")
    while True:
        topic, message = subscriber.recv_string().split(' ', 1)
        event_data = json.loads(message)
        product_id = event_data['product_id']
        
        # Initialisation du prix à 0.0 pour ce nouveau produit
        uow = UnitOfWork(session_factory)
        with uow as u:
            repo = PriceRepository(u.session)
            repo.add_default_price(product_id)
            print(f"[Pricing] Initialized price for product {product_id}")

# --- LOGIQUE ZMQ REP (Répond à la Gateway pour get-price) ---
def start_zmq_responder():
    context = zmq.Context()
    responder = context.socket(zmq.REP)
    responder.bind("tcp://*:5556") # Port d'écoute pour la Gateway
    
    print("[Pricing] ZMQ Responder started on port 5556...")
    while True:
        request = responder.recv_json()
        product_id = request.get('product_id')
        
        uow = UnitOfWork(session_factory)
        with uow as u:
            repo = PriceRepository(u.session)
            price = repo.get_by_product_id(product_id)
            responder.send_json({"product_id": str(product_id), "price": price.value if price else 0.0})

# Lancement des threads ZMQ au démarrage
threading.Thread(target=start_zmq_subscriber, daemon=True).start()
threading.Thread(target=start_zmq_responder, daemon=True).start()

@app.get("/health")
def health():
    return {"status": "Pricing Service is healthy"}

if __name__ == "__main__":
    import threading
    import uvicorn

    # 1. On connecte la DB (une seule fois)
    if connect_db():
        # 2. On lance les threads ZMQ ICI et seulement ici
        print("[Pricing] Starting ZMQ Subscriber thread...")
        threading.Thread(target=start_zmq_subscriber, daemon=True).start()
        
        # 3. On lance FastAPI/Uvicorn. C'est lui qui va "bloquer" le container
        # IMPORTANT : Ne mets pas reload=True ici dans Docker
        print("[Pricing] Starting FastAPI server...")
        uvicorn.run(app, host="0.0.0.0", port=8000)