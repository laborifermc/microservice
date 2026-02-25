import pika
from fastapi import FastAPI, HTTPException
from uuid import UUID
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from infrastructure.db.models import Base
from infrastructure.db.uows import UnitOfWork
from application.services import ProductApplicationService
from application.dtos import ProductCreateDTO

app = FastAPI()

# Database Setup
engine = create_engine("postgresql://user:password@db:5432/product_db")
Base.metadata.create_all(bind=engine)
session_factory = sessionmaker(bind=engine)

# RabbitMQ Setup (On ignore les erreurs si MQ n'est pas prêt pour l'exemple)
try:
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='rabbitmq'))
    channel = connection.channel()
    channel.exchange_declare(exchange='product_events', exchange_type='topic')
except:
    channel = None

def get_service():
    return ProductApplicationService(UnitOfWork(session_factory), channel)

@app.post("/products")
def create(data: ProductCreateDTO):
    return get_service().create_product(data)

@app.get("/products")
def list_all():
    return get_service().get_all_products()

@app.get("/products/{id}")
def get_one(id: UUID):
    prod = get_service().get_product(id)
    if not prod: raise HTTPException(status_code=404)
    return prod

@app.put("/products/{id}")
def update(id: UUID, data: ProductCreateDTO):
    prod = get_service().update_product(id, data)
    if not prod: raise HTTPException(status_code=404)
    return prod

@app.delete("/products/{id}")
def delete(id: UUID):
    if not get_service().delete_product(id): raise HTTPException(status_code=404)
    return {"status": "deleted"}