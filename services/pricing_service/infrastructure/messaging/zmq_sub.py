import zmq, json, threading

def start_subscriber(service_callback):
    context = zmq.Context()
    socket = context.socket(zmq.SUB)
    # On se connecte au Product Service (Port 5555 défini précédemment)
    socket.connect("tcp://product-service:5555")
    socket.setsockopt_string(zmq.SUBSCRIBE, "ProductCreatedEvent")

    def listen():
        while True:
            topic, message = socket.recv_string().split(' ', 1)
            data = json.loads(message)
            print(f"[Pricing] Received event: {topic}")
            service_callback(data['product_id'])

    threading.Thread(target=listen, daemon=True).start()