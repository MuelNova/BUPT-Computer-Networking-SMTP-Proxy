from abc import ABC, abstractmethod
from typing import Any, Tuple, Dict


class BaseParser(ABC):
    @classmethod
    @abstractmethod
    def parse(data: bytes) -> Any:
        raise NotImplementedError


class HTTPParser(BaseParser):
    @classmethod
    def parse(cls, data: bytes) -> Tuple[str, Dict[str, Any]]:
        """
        ('METHOD', {'key', 'value'})
        """
        ...
        

