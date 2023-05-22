import socket
from abc import ABC, abstractclassmethod
from datetime import datetime
from typing import Any, Type, Optional

from app.config import get_config
from app.models import HTTPParseModel, PathModel, QQMailPostModel
from app.smtp_forwarder import get_smtp_forwarder
from app.parser import HTTPParser
from app.logging import logger


config = get_config()

class BaseHTTPHandler(ABC):
    def __init__(self, parser: Type[HTTPParser]):
        if not issubclass(parser, HTTPParser):
            raise TypeError(f'parser must be a subclass of {HTTPParser.__name__}')
        self.parser = parser

    def __call__(self, server: socket.socket, client: socket.socket, data: bytes) -> Any:
        res = self.parser.parse(data)
        return getattr(self, f'do_{res.method}')(server, client, res)

    @abstractclassmethod
    def do_CONNECT(self, server: socket.socket, client: socket.socket, data: HTTPParseModel) -> Any:
        raise NotImplementedError

    @abstractclassmethod
    def do_GET(self, server: socket.socket, client: socket.socket, data: HTTPParseModel) -> Any:
        raise NotImplementedError

    @abstractclassmethod
    def do_POST(self, server: socket.socket, client: socket.socket, data: HTTPParseModel) -> Any:
        raise NotImplementedError

    @abstractclassmethod
    def do_PATCH(self, server: socket.socket, client: socket.socket, data: HTTPParseModel) -> Any:
        raise NotImplementedError

    @abstractclassmethod
    def do_OPTION(self, server: socket.socket, client: socket.socket, data: HTTPParseModel) -> Any:
        raise NotImplementedError

    @abstractclassmethod
    def do_PUT(self, server: socket.socket, client: socket.socket, data: HTTPParseModel) -> Any:
        raise NotImplementedError

    @abstractclassmethod
    def do_DELETE(self, server: socket.socket, client: socket.socket, data: HTTPParseModel) -> Any:
        raise NotImplementedError
    
    @abstractclassmethod
    def make_session(self, client: socket.socket, path: PathModel) -> Optional[socket.socket]:
        raise NotImplementedError


class HTTPHandler(BaseHTTPHandler):
    def do_CONNECT(self, server: socket.socket, client: socket.socket, data: HTTPParseModel) -> Any:
        cc = self.make_session(client, data.path)
        if not cc:
            return 
        client.send(b"HTTP/1.1 200 Connection established\r\n\r\n")
        client.setblocking(0)
        cc.setblocking(0)
        while True:
            try:
                reply = client.recv(2**13)
                if not reply: 
                    break
                cc.send(reply)
            except:
                pass
                
            try:
                reply = cc.recv(2**13)
                if not reply:
                    break
                client.send(reply)
            except:
                pass  # We don't handle exceptions here because the lack of time
        cc.shutdown(socket.SHUT_RDWR)
        cc.close()
        client.close()
        return
    
    def do_GET(self, server: socket.socket, client: socket.socket, data: HTTPParseModel) -> Any:
        return self.basic_FORWARD(server, client, data, 'GET')
    
    def do_POST(self, server: socket.socket, client: socket.socket, data: HTTPParseModel) -> Any:
        return self.basic_FORWARD(server, client, data, 'POST')
    
    def do_PATCH(self, server: socket.socket, client: socket.socket, data: HTTPParseModel) -> Any:
        return self.basic_FORWARD(server, client, data, 'PATCH')
    
    def do_OPTION(self, server: socket.socket, client: socket.socket, data: HTTPParseModel) -> Any:
        return self.basic_FORWARD(server, client, data, 'OPTION')
    
    def do_PUT(self, server: socket.socket, client: socket.socket, data: HTTPParseModel) -> Any:
        return self.basic_FORWARD(server, client, data, 'PUT')
    
    def do_DELETE(self, server: socket.socket, client: socket.socket, data: HTTPParseModel) -> Any:
        return self.basic_FORWARD(server, client, data, 'DELETE')
    
    def make_session(self, client: socket.socket, path: PathModel) -> Optional[socket.socket]:
        cc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            cc.connect((path.webserver, path.port))
        except Exception as e:
            logger.error(f'Cannot connect to {path.raw_path}, {e}')
            cc.close()
            client.send(b'HTTP/1.1 502 Bad Gateway\r\n\r\n')
            client.close()
            return None
        return cc
    
    def basic_FORWARD(self, server: socket.socket, client: socket.socket, data: HTTPParseModel, method: str) -> Any:
        cc = self.make_session(client, data.path)
        if not cc:
            return 
        cc.send(data.raw)
        while True:
            buf = cc.recv(1024)
            logger.debug(f'[HTTPHandler] {method} | {data.path.raw_path} | {buf}')
            client.send(buf)
            if not buf:
                break
        cc.shutdown(socket.SHUT_RDWR)
        cc.close()
        client.close()
        return
    

class SMTPProxyHandler(HTTPHandler):
    def do_POST(self, server: socket.socket, client: socket.socket, data: HTTPParseModel) -> Any:
        if data.path.webserver == config.QQ_MAIL_WEBSERVER and data.path.path == config.QQ_MAIL_POST_URL:
            # 将 SMTP 交由 SMTPHandler 处理
            param = dict(p.split('=') for p in data.body.decode('utf-8').split('&'))
            try:
                param = QQMailPostModel(**param, socket=client)
            except ValueError as e:
                client.send(b'HTTP/1.1 400 Bad Request\r\n\r\n')
                logger.error(f'{e}')
                client.close()
                return
            get_smtp_forwarder().add_forwarder(param)
        else:
            super().do_POST(server, client, data)

