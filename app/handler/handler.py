import socket
from abc import ABC, abstractclassmethod
from typing import Any

from ..parser import HTTPParser


class BaseHTTPHandler(ABC):
    def __init__(self, parser: HTTPParser):
        if not issubclass(parser, HTTPParser):
            raise TypeError(f'parser must be a subclass of {HTTPParser.__name__}')
        self.parser = parser

    def __call__(self, server: socket.socket, client: socket.socket, data: bytes) -> Any:
        type_, result = self.parser.parse(data)
        return getattr(self, f'do_{type_}')(server, client, **result)

    @abstractclassmethod
    def do_CONNECT(self, server: socket.socket, client: socket.socket, **kwargs: Any) -> Any:
        raise NotImplementedError

    @abstractclassmethod
    def do_GET(self, server: socket.socket, client: socket.socket, **kwargs: Any) -> Any:
        raise NotImplementedError

    @abstractclassmethod
    def do_POST(self, server: socket.socket, client: socket.socket, **kwargs: Any) -> Any:
        raise NotImplementedError

    @abstractclassmethod
    def do_PATCH(self, server: socket.socket, client: socket.socket, **kwargs: Any) -> Any:
        raise NotImplementedError

    @abstractclassmethod
    def do_OPTION(self, server: socket.socket, client: socket.socket, **kwargs: Any) -> Any:
        raise NotImplementedError

    @abstractclassmethod
    def do_PUT(self, server: socket.socket, client: socket.socket, **kwargs: Any) -> Any:
        raise NotImplementedError

    @abstractclassmethod
    def do_DELETE(self, server: socket.socket, client: socket.socket, **kwargs: Any) -> Any:
        raise NotImplementedError


class SMTPProxyHandler(BaseHTTPHandler):
    def do_CONNECT(self, server: socket.socket, client: socket.socket, **kwargs: Any) -> Any:
        pass

    def do_GET(self, server: socket.socket, client: socket.socket, **kwargs: Any) -> Any:
        pass

    def do_POST(self, server: socket.socket, client: socket.socket, domain: str, **kwargs: Any) -> Any:
        if domain == 'smtp.qq.com':
            ...
        else:
            ...

    do_PATCH = do_GET
    do_OPTION = do_GET
    do_PUT = do_GET
    do_DELETE = do_GET
