import argparse
import asyncio
import server
import request_handler

import logger

log = logger.setup_logger('main.log')

def run(args: argparse.Namespace):
    log.info(f"{args}")
    nth_prime_handler = request_handler.NthPrimeRequestHandler
    nth_prime_handler.use_process_pool = args.use_process_pool
    tserver = server.ThreadedServer(args.host, args.port, use_threads=args.use_threads)
    tserver.request_handler = nth_prime_handler
    tserver.start()

# uncomment to run async

# def run(args: argparse.Namespace):
#     log.info(f"{args}")
#     nth_prime_handler = request_handler.AsyncNthPrimeRequestHandler
#     nth_prime_handler.use_process_pool = args.use_process_pool
#     threaded_server = server.AsyncServer(args.host, args.port)
#     threaded_server.server_socket.setblocking(False)
#     server.request_handler = nth_prime_handler
#     loop = asyncio.get_event_loop()
#     loop.create_task(server.start())
#     loop.run_forever()




if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Socket client")
    parser.add_argument("--host", type=str, default="localhost", help="Server address")
    parser.add_argument("--port", type=int, default=8000, help="Server port")
    parser.add_argument(
        "--use-threads",
        action="store_true",
        help="Use threads instead to handle requests",
    )
    parser.add_argument(
        "--use-process-pool",
        action="store_true",
        help="Use process pool executor to speed up computation",
    )
    args = parser.parse_args()
    run(args)
