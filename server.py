import abc
import asyncio
import socket
import threading

import logger
import request_handler
import utils

log = logger.setup_logger("server.log")


class AbstractServer(abc.ABC):
    _request_handler: request_handler.SocketRequestHandler = None
    _is_running: bool = False
    _server_socket: socket.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    _backlog: int = 5

    @property
    def server_socket(self):
        return self._server_socket

    @server_socket.setter
    def server_socket(self, value: socket.socket):
        utils.raise_for_type(value, socket.socket)
        self._server_socket = value

    @server_socket.getter
    def server_socket(self):
        return self._server_socket

    @property
    def request_handler(self):
        return self._request_handler

    @request_handler.setter
    def request_handler(self, value):
        if not issubclass(value, request_handler.SocketRequestHandler):
            raise TypeError(
                "request_handler should be a sub class of SocketRequestHandler"
            )
        self._request_handler = value

    @request_handler.getter
    def request_handler(self):
        return self._request_handler

    @property
    def backlog(self):
        return self._backlog

    @backlog.setter
    def backlog(self, value):
        utils.raise_for_type(value, int)
        if value < 0:
            raise ValueError("backlog value should be greater than 0")
        self._backlog = value

    @backlog.getter
    def backlog(self):
        return self._backlog


class ThreadedServer(AbstractServer):
    def __init__(self, host, port, use_threads: bool = False):
        self.host = host
        self.port = port
        self.use_threads = use_threads

    def _init_server(self):
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(self.backlog)
        self._is_running = True
        if not self.request_handler:
            raise ValueError("Request handler not set")
        log.info(f"Server listening on {self.host}:{self.port}...")

    def _start(self):
        client_socket, client_address = self.server_socket.accept()
        handler_obj = self.request_handler()
        handler_obj.client_socket = client_socket
        if self.use_threads:
            thread = threading.Thread(target=handler_obj.handle, daemon=True)
            thread.start()
            log.info(f"Active thread counts - {threading.active_count()}")
        else:
            handler_obj.handle()
        log.info(f"Received connection from {client_address[0]}:{client_address[1]}")

    def start(self):
        self._init_server()
        try:
            while self._is_running:
                self._start()
        except KeyboardInterrupt as err:
            log.info(f"Keyboard interrupt - {err}")
            log.info("Stopping the server")
            self.stop()

    def stop(self):
        self._is_running = False
        if self.server_socket:
            self.server_socket.close()
        log.info("Connection closed")

class AsyncServer:
    _loop: asyncio.AbstractEventLoop = asyncio.get_event_loop()

    def __init__(self, host, port):
        self.host = host
        self.port = port

    def _init_server(self):
        if not self.request_handler:
            raise ValueError("Request handler not set")
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(self.backlog)
        self._is_running = True
        self.request_handler.event_loop = self._loop
        log.info(f"Server listening on {self.host}:{self.port}...")

    async def start(self):
        self._init_server()
        try:
            while self._is_running:
                client, _ = await self._loop.sock_accept(self.server_socket)
                handler_obj = self.request_handler()
                handler_obj.client_socket = client
                self._loop.create_task(handler_obj.handle())
        except KeyboardInterrupt as err:
            log.info(f"Keyboard interrupt - {err}")
            log.info("Stopping the server")
            self.stop()

    def stop(self):
        self._is_running = False
        if self.server_socket:
            self.server_socket.close()
        log.info("Connection closed")


