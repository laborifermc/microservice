import zmq, json, threading
from fastapi import FastAPI
from uuid import UUID
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import OperationalError
import time

from infrastructure.db.models import Base
from infrastructure.db.uows import UnitOfWork
from infrastructure.db.repositories import CustomerRepository
from infrastructure.messaging.zmq_pub import CustomerPublisher
from domain.models import Customer

app = FastAPI()
DATABASE_URL = "postgresql://db_user:password@db:5432/customer_db"
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

# Publisher pour notifier les autres (Order, etc.)
pub = CustomerPublisher(port=5559)

def start_responder():
    context = zmq.Context()
    socket = context.socket(zmq.REP)
    socket.bind("tcp://*:5558")
    
    print("[Customer] Responder ready on 5558")
    while True:
        req = socket.recv_json()
        uow = UnitOfWork(session_factory)
        
        with uow as u:
            repo = CustomerRepository(u.session)
            if req['action'] == "create":
                new_cust = Customer(**req['data'])
                repo.add(new_cust)
                # On publie l'événement après la création en DB
                pub.publish_customer_created(new_cust)
                socket.send_json(json.loads(new_cust.model_dump_json()))
            
            elif req['action'] == "get_one":
                cust = repo.get_by_id(UUID(req['id']))
                socket.send_json(json.loads(cust.model_dump_json()) if cust else {"error": "not_found"})

if __name__ == "__main__":
    # On bloque sur le responder
    if connect_db():start_responder()