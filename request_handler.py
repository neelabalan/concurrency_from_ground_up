import abc
import asyncio
import concurrent.futures as concurrent
import threading
import socket

import logger
import utils

log = logger.setup_logger('request_handler.log')

class RequestHandler(abc.ABC):
    @abc.abstractmethod
    def handle(self):
        ...


class SocketRequestHandler(RequestHandler):
    _client_socket: socket.socket
    _recv_bytes: int = 1024

    @property
    def client_socket(self):
        ...

    @client_socket.setter
    def client_socket(self, value: socket.socket):
        utils.raise_for_type(value, socket.socket)
        self._client_socket = value

    @client_socket.getter
    def client_socket(self) -> socket.socket:
        return self._client_socket

    @property
    def recv_bytes(self):
        ...

    @recv_bytes.setter
    def recv_bytes(self, value: int):
        utils.raise_for_type(value, int)
        if not value > 0:
            raise ValueError("recv_bytes should be greater than 0")
        self._recv_bytes = value

    @recv_bytes.getter
    def recv_bytes(self) -> int:
        return self._recv_bytes


class NthPrimeRequestHandler(SocketRequestHandler):
    use_process_pool: bool
    _process_pool = concurrent.ProcessPoolExecutor()

    def handle(self):
        while True:
            data = self.client_socket.recv(self.recv_bytes)
            if not data:
                break
            try:
                number = int(utils.bytes_to_str(data))
                result = self.compute(number)
                response = utils.str_to_bytes(str(result)) + b"\n"
            except ValueError as ex:
                response = utils.str_to_bytes(f"Invalid number - {ex}\n")
            except ConnectionResetError as ex:
                log.error(f"Connection reset - {ex}")
            self.client_socket.sendall(response)
        # once done handling requests the connection can be closed
        log.info(f"Connection closed from {threading.current_thread().name}")
        self.client_socket.close()

    def _is_prime(self, number: int):
        if number <= 1:
            return False
        for n in range(2, int(number**0.5) + 1):
            if number % n == 0:
                return False
        return True

    def compute(self, number: int) -> int:
        if self.use_process_pool:
            future = self._process_pool.submit(self._compute, number)
            return future.result()
        else:
            return self._compute(number)

    def _compute(self, number: int):
        prime_count = 0
        n = 2
        while prime_count < number:
            if self._is_prime(n):
                prime_count += 1
                if prime_count == number:
                    return n
            n += 1

class AsyncNthPrimeRequestHandler(NthPrimeRequestHandler):
    use_process_pool: bool
    _loop: asyncio.AbstractEventLoop
    _process_pool = concurrent.ProcessPoolExecutor()

    @property
    def event_loop(self):
        return self._loop

    @event_loop.setter
    def event_loop(self, value):
        self._loop = value

    async def handle(self):
        while True:
            data = await self.event_loop.sock_recv(self.client_socket, self.recv_bytes)
            if not data:
                break
            try:
                number = int(utils.bytes_to_str(data))
                result = self.compute(number)
                response = utils.str_to_bytes(str(result)) + b"\n"
            except ValueError as ex:
                response = utils.str_to_bytes(f"Invalid number - {ex}\n")
            except ConnectionResetError as ex:
                log.error(f"Connection reset - {ex}")
            await self.event_loop.sock_sendall(self.client_socket, response)
        # once done handling requests the connection can be closed
        self.client_socket.close()

