import socket
from abc import ABC, abstractmethod
from typing import Tuple

class BasicParser(ABC):
    client: socket.socket
    address: Tuple[str, int]
    @abstractmethod
    def __init__(self, client: socket.socket, address: Tuple[str, int], *args, **kwargs):
        self.client = client
        self.address = address

    @abstractmethod
    def parse(self, data: bytes) -> dict:  # return a smtp model
        pass


class ParserFactory:
    @staticmethod
    def __call__(client: socket.socket, address: Tuple[str, int], data: bytes):
        ...
