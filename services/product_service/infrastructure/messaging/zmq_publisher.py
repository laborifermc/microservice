# services/Product-service/infrastructure/messaging/zmq_publisher.py
import zmq
import json

class ZmqPublisher:
    def __init__(self, port=5555):
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.PUB)
        # Le Product-service "bind" (serveur), les autres se "connect"
        self.socket.bind(f"tcp://*:{port}")

    def handle_event(self, event):
        # On transforme l'événement Pydantic en JSON
        topic = event.__class__.__name__
        message = event.model_dump_json()
        
        # ZMQ PUB envoie : "Topic Message"
        print(f"[ZMQ] Publishing to topic {topic}: {message}")
        self.socket.send_string(f"{topic} {message}")