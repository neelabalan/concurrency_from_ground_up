import argparse
import socket

import logger
import utils

log = logger.setup_logger("logs/perf1.log")


@utils.measure_time
def send_and_receive(number: int, sock: socket.socket) -> bytes:
    sock.send(str(number).encode("ascii"))
    resp = sock.recv(100)
    return resp


def run(host: str, port: int, number: int, repeat: int = 1):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((host, port))
    for _ in range(repeat):
        resp = send_and_receive(number, sock)
        log.info(utils.bytes_to_str(resp))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Socket client")
    parser.add_argument("--host", type=str, default="localhost", help="Server address")
    parser.add_argument("--port", type=int, default=8000, help="Server port")
    parser.add_argument("--number", type=int, default=13, help="Nth prime number")
    parser.add_argument(
        "--repeat",
        type=int,
        default=1,
        help="Number of times the operation has to repeat",
    )
    args = parser.parse_args()
    run(host=args.host, port=args.port, number=args.number, repeat=args.repeat)
