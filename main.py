from typing import Any
from app import logger, Proxy
from app.handler import SMTPProxyHandler
from app.parser import HTTPParser

proxy = Proxy(SMTPProxyHandler, HTTPParser, host='0.0.0.0')
proxy()

