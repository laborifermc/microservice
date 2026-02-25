import zmq, json, threading

def start_responder(get_stock_callback):
    context = zmq.Context()
    socket = context.socket(zmq.REP)
    socket.bind("tcp://*:5556") # Port pour les requêtes entrantes

    def run():
        while True:
            request = socket.recv_json()
            # On cherche le stock en base via le callback
            stock = get_stock_callback(request['product_id'])
            socket.send_json({"product_id": request['product_id'], "stock": stock})

    threading.Thread(target=run, daemon=True).start()