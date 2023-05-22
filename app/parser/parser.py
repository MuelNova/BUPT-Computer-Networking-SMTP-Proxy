from abc import ABC, abstractmethod
from typing import Any, Tuple, Dict, List

from app.models import HTTPParseModel, PathModel, SMTPParseModel
from app.logging import logger


class BaseParser(ABC):
    @classmethod
    @abstractmethod
    def parse(data: bytes) -> Any:
        raise NotImplementedError


class HTTPParser(BaseParser):
    @classmethod
    def parse(cls, data: bytes) -> HTTPParseModel:
        """
        ('METHOD', {'key', 'value'})
        """
        logger.debug(f'[HTTPParser] Received data: {data}')   
        method, *headers, body= data.split(b'\r\n')
        method, path, version = method.decode('utf-8').split(' ')
        path = cls.parse_path(path)
        headers = dict([header.decode('utf-8').split(': ') for header in headers[:-1]])
        return HTTPParseModel(raw=data, method=method, path=path, version=version, headers=headers, body=body)
    
    @classmethod
    def parse_path(cls, raw_path: str) -> PathModel:
        if len(splitted_path := raw_path.split('://')) == 1:
            protocol = None
            tmp_uri = splitted_path[0]
        else:
            protocol, tmp_uri = splitted_path
        
        webserver = tmp_uri.split('/')[0]
        path = tmp_uri[len(webserver): (port_idx := tmp_uri.find(':'))]
        query = ''
        if path.find('?') != -1:
            path, query = path.split('?')
        if port_idx != -1:
            port = tmp_uri[port_idx + 1:]
            webserver = tmp_uri[:port_idx]
        else:
            port = 80
        return PathModel(raw_path=raw_path, protocol=protocol, webserver=webserver, path=path, query=query, port=port)
        

class SMTPParser(BaseParser):
    @classmethod
    def parse(cls, data: bytes) -> SMTPParseModel:
        logger.debug(f'[SMTPParser] Received data: {data}')
        status_code, message = data[:3], data[4:]
        status_code = int(status_code)
        return SMTPParseModel(raw=data, status_code=status_code, message=message)
    
    @classmethod
    def parse_multi(cls, data: bytes) -> List[SMTPParseModel]:
        return [cls.parse(d) for d in data.split(b'\r\n') if d != b'']