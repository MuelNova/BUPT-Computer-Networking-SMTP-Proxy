import socket
import sys
import threading
import time
import signal
from typing import Type, Any, Tuple, List

# 导入日志记录
from app.logging import logger
# 导入基本HTTP处理程序
from app.handler import BaseHTTPHandler
# 导入基本解析器和HTTP解析器
from app.parser import BaseParser, HTTPParser

class Proxy:
    # 初始化代理类
    def __init__(self,
                 handler: Type[BaseHTTPHandler],
                 parser: Type[BaseParser] = HTTPParser,
                 *,
                 host: str = 'localhost',
                 port: int = 8080,
                 max_conn: int = 32,
                 timeout: int = 5
                 ):
        # 初始化处理程序实例
        self.handler = handler(parser)

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # ipv4, tcp
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind((host, port))
        self.socket.listen(max_conn)

        self.timeout = timeout


    # 运行代理，接受连接并启动数据处理线程
    def run(self):
        while True:
            client, address = self.socket.accept()
            logger.debug(f'{self} New connection from {address}')
            thread = threading.Thread(target=self.handle_data, args=[client])
            thread.daemon = True
            thread.start()

    # 启动多请求处理线程，并捕获中断信号以关闭代理
    def __call__(self):
        logger.info(f'{self} Starting...')
        start_multirequest = threading.Thread(target=self.run)
        start_multirequest.daemon = True
        start_multirequest.start()
        while True:
            time.sleep(0.01)
            signal.signal(signal.SIGINT, self.close)

    # 返回代理类实例的字符串表示
    def __repr__(self):
        return f'<Proxy {self.socket.getsockname()}>'
        
    # 处理客户端数据，调用处理程序实例处理数据, 并在超时情况下关闭连接
    def handle_data(self, client: socket.socket):
        try:
            data = client.recv(65536)
        except socket.timeout:
            logger.debug(f'{client} Connection timed out')
            client.close()
            return
        self.handler(self.socket, client, data)
        
    # 关闭代理并退出程序

    def close(self, *args):
        logger.info(f'{self} Closing...')
        self.socket.close()
        logger.info(f'All proxies closed')
        sys.exit(0)
        

