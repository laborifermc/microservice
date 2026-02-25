import zmq, json, time
from uuid import UUID
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from infrastructure.db.models import Base
from infrastructure.db.uows import UnitOfWork
from infrastructure.db.repositories import OrderRepository
from domain.models import Order

DATABASE_URL = "postgresql://db_user:password@db:5432/order_db"
engine = create_engine(DATABASE_URL)
session_factory = sessionmaker(bind=engine)

def start_order_responder():
    context = zmq.Context()
    
    # PUB pour les événements (doit être bindé une seule fois)
    publisher = context.socket(zmq.PUB)
    publisher.bind("tcp://*:5561")
    
    # REP pour la Gateway
    responder = context.socket(zmq.REP)
    responder.bind("tcp://*:5560")
    
    print("[Order] Responder on 5560, Publisher on 5561")
    
    while True:
        req = responder.recv_json()
        if req['action'] == "create_order":
            with UnitOfWork(session_factory) as u:
                repo = OrderRepository(u.session)
                new_order = Order(**req['data'])
                repo.create_order(new_order)
                
                # Envoi des événements pour chaque ligne
                for line in new_order.lines:
                    event = {
                        "product_id": str(line.product_id), 
                        "quantity": int(line.quantity)
                    }
                    publisher.send_string(f"OrderLineCreatedEvent {json.dumps(event)}")
                    print(f"[Order] Published OrderLineCreatedEvent for product {line.product_id}")
                
                # On renvoie la réponse à la Gateway
                responder.send_json(json.loads(new_order.model_dump_json()))

if __name__ == "__main__":
    time.sleep(5) # Attente sécu DB
    Base.metadata.create_all(bind=engine)
    start_order_responder()