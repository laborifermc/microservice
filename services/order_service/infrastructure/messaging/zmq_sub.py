import zmq, json, threading

class OrderSubscriber:
    def __init__(self):
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.SUB)

    def subscribe_to_sources(self):
        # S'abonne au Product Service
        self.socket.connect("tcp://product-service:5555")
        self.socket.setsockopt_string(zmq.SUBSCRIBE, "ProductCreatedEvent")
        
        # S'abonne au Customer Service
        self.socket.connect("tcp://customer-service:5559")
        self.socket.setsockopt_string(zmq.SUBSCRIBE, "CustomerCreatedEvent")

    def start_listening(self):
        def loop():
            while True:
                raw = self.socket.recv_string()
                topic, payload = raw.split(' ', 1)
                data = json.loads(payload)
                print(f"[Order-SUB] Received {topic} for ID: {data.get('id') or data.get('customer_id')}")
                # Ici tu pourrais mettre à jour un cache local de produits/clients
        
        threading.Thread(target=loop, daemon=True).start()