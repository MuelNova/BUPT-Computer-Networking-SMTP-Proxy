import socket
import threading
from typing import Type, Any, Tuple, List

from ..logging import logger
from ..handler import BaseHTTPHandler
from ..parser import BaseParser, HTTPParser

class Proxy:
    def __init__(self,
                 handler: Type[BaseHTTPHandler],
                 parser: Type[BaseParser] = HTTPParser,
                 *,
                 host: str = 'localhost',
                 port: int = 8080,
                 max_conn: int = 32,
                 buf_size: int = 2**13,
                 timeout: int = 5
                 ):
        
        self.handler = handler(parser)

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # ipv4, tcp
        self.socket.bind((host, port))
        self.socket.listen(max_conn)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        self.buf_size = buf_size
        self.timeout = timeout

        self.threads: List[threading.Thread] = []
        self.clients: List[socket.socket] = []

    
    def run(self):
        while True:
            try:
                client, address = self.socket.accept()
                client.settimeout(self.timeout)
                logger.info(f'{self} New connection from {address}')
                thread = threading.Thread(target=self.handle_data, args=(client, address))
                self.threads.append(thread)
                self.clients.append(client)
                thread.start()
            except KeyboardInterrupt:
                self.close()
                break


    def __call__(self):
        try:
            logger.info(f'{self} Started, waiting for connection...')
            self.run()
        except KeyboardInterrupt:
            self.close()

    
    def __repr__(self):
        return f'<Proxy {self.socket.getsockname()}>'
        

    def handle_data(self, client: socket.socket):
        data = client.recv(self.buf_size)
        self.handler(self.socket, client, data)
        

    def close(self):
        logger.info(f'{self} Closing...')
        for thread in self.threads:
            thread.join()
        for client in self.clients:
            client.close()
        self.socket.close()

