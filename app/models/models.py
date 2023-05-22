import socket
import re
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field, validator

class PathModel(BaseModel):
    raw_path: str
    protocol: Optional[str] = None
    webserver: str
    path: str
    query: str = ''
    port: int


class HTTPParseModel(BaseModel):
    raw: bytes
    method: str
    path: PathModel
    version: str
    headers: Dict[str, Any]
    body: Optional[bytes] = None


class ToModel(BaseModel):
    address: str
    name: str

    class Config:
        validate_assignment = True

    @validator('name', pre=True, always=True)
    def name_validator(cls, value: Optional[str], values: Dict[str, str]) -> str:
        if not value:
            return values['address'].split('@')[0]
        return value

class QQMailPostModel(BaseModel):
    to: List[ToModel]
    sendmailname: str
    subject: str
    content: str = Field(..., alias="content__html")
    socket: socket.socket

    class Config:
        arbitrary_types_allowed = True

    @validator('to', pre=True, always=True)
    def to_validator(cls, value: str) -> List[ToModel]:
        value = value.split('; ')
        res = []
        for i in value:
            name = ''
            address = ''
            i = i.replace("%22", '')
            pattern = re.search(r"(.+?)<(.+?)>", i)
            if pattern:
                name = pattern.group(1)
                address = pattern.group(2)
            
            if not address:
                 address = i
            if re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', address) is None:
                raise ValueError(f'Invalid address: {address}')
            res.append(ToModel(name=name, address=address))
        return res