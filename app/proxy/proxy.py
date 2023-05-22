import socket
import sys
import threading
import time
import signal
from typing import Type, Any, Tuple, List

from app.logging import logger
from app.handler import BaseHTTPHandler
from app.parser import BaseParser, HTTPParser

class Proxy:
    def __init__(self,
                 handler: Type[BaseHTTPHandler],
                 parser: Type[BaseParser] = HTTPParser,
                 *,
                 host: str = 'localhost',
                 port: int = 8080,
                 max_conn: int = 32,
                 timeout: int = 5
                 ):
        
        self.handler = handler(parser)

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # ipv4, tcp
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind((host, port))
        self.socket.listen(max_conn)

        self.timeout = timeout


    
    def run(self):
        while True:
            client, address = self.socket.accept()
            logger.debug(f'{self} New connection from {address}')
            thread = threading.Thread(target=self.handle_data, args=[client])
            thread.daemon = True
            thread.start()


    def __call__(self):
        logger.info(f'{self} Starting...')
        start_multirequest = threading.Thread(target=self.run)
        start_multirequest.daemon = True
        start_multirequest.start()
        while True:
            time.sleep(0.01)
            signal.signal(signal.SIGINT, self.close)

    
    def __repr__(self):
        return f'<Proxy {self.socket.getsockname()}>'
        

    def handle_data(self, client: socket.socket):
        try:
            data = client.recv(1024)
        except socket.timeout:
            logger.debug(f'{client} Connection timed out')
            client.close()
            return
        self.handler(self.socket, client, data)
        

    def close(self, *args):
        logger.info(f'{self} Closing...')
        self.socket.close()
        logger.info(f'All proxies closed')
        sys.exit(0)
        

