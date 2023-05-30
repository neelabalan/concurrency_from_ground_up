import argparse
import socket
import threading
import time

import logger
import utils

log = logger.setup_logger("logs/perf2.log")


class RequestSimulator:
    _req: int = 0

    def __init__(self, sock: socket.socket, number: int = 1):
        self.socket = sock
        self.number = number

    @property
    def requests(self):
        ...

    @requests.setter
    def requests(self, value):
        utils.raise_for_type(value, int)
        if not value >= 0:
            raise ValueError("requests value should be greater or equal to 0")
        self._req = value

    @requests.getter
    def requests(self):
        return self._req

    def simulate(self):
        # randomize?
        _number = utils.str_to_bytes(str(self.number))
        while True:
            self.socket.send(_number)
            _ = self.socket.recv(1024)
            self.requests += 1


def monitor(simulator: RequestSimulator):
    while True:
        time.sleep(1)
        log.info(f"{simulator.requests} reqs/sec")
        simulator.requests = 0


def run(host: str, port: int, number: int):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((host, port))
    simulator = RequestSimulator(sock, number)
    simulator_thread = threading.Thread(target=simulator.simulate)
    monitor_thread = threading.Thread(target=monitor, args=(simulator,))

    simulator_thread.start()
    monitor_thread.start()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Socket client")
    parser.add_argument("--host", type=str, default="localhost", help="Server address")
    parser.add_argument("--port", type=int, default=8000, help="Server port")
    parser.add_argument("--number", type=int, default=13, help="Nth prime")
    args = parser.parse_args()
    run(host=args.host, port=args.port, number=args.number)
