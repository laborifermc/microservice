import zmq

class ZmqClient:
    def __init__(self, host, port):
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.REQ)
        self.socket.connect(f"tcp://{host}:{port}")

    def request(self, data: dict):
        self.socket.send_json(data)
        return self.socket.recv_json()