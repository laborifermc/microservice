import zmq, json

class CustomerPublisher:
    def __init__(self, port=5559):
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.PUB)
        self.socket.bind(f"tcp://*: {port}")

    def publish_customer_created(self, customer):
        topic = "CustomerCreatedEvent"
        message = customer.model_dump_json()
        self.socket.send_string(f"{topic} {message}")
        print(f"[Customer] Event published: {topic}")