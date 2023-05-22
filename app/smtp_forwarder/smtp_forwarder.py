import queue
import base64
import socket
import threading
from typing import Type, Any
from abc import ABC, abstractmethod

from app.exceptions.smtp import *
from app.models import MailPostModel, QQMailPostModel
from app.parser import SMTPParser
from app.logging import logger
from app.config import get_config, AccountConfig

class BaseSMTPForwarder(ABC):
    def __init__(self,
                 data: MailPostModel,
                 type_: str,
                 *,
                 parser: Type[SMTPParser] = SMTPParser):
        if (config := next(filter(lambda x: x.type == type_, get_config().accounts), None)) is None:
            raise ValueError(f"No {type_} SMTP account found")
        self.config: AccountConfig = config
        self.socket = None
        self.server_socket = data.socket
        self.content = data
        self.parser = parser
    
    @abstractmethod
    def send(self):
        raise NotImplementedError


class QQMailSMTPForwarder(BaseSMTPForwarder):
    def __init__(self, data: QQMailPostModel, *, parser: Type[SMTPParser] = SMTPParser):
        super().__init__(data, "qq", parser=parser)

    def send(self):
        """
        实现的异常处理：
            1. 连接超时
            2. 用户名密码错误
            3. 发送邮件失败
            4. 用户名不存在
        """
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.socket.connect((self.config.smtp_server, self.config.smtp_port))
        except socket.timeout:
            raise SMTPConnectionError(f"Connection timeout while connecting to SMTP server {self.config.smtp_server}:{self.config.smtp_port}")
        
        first = self.parser.parse(self.socket.recv(1024))
        if first.status_code != 220:
            raise SMTPConnectionError(f"[{first.status_code}] {first.message}")
        
        self.socket.send(f"EHLO {self.config.smtp_server}\r\n".encode('utf-8'))
        seconds = self.parser.parse_multi(self.socket.recv(1024))
        if seconds[-1].status_code != 250:
            raise SMTPConnectionError(f"【HELO】 [{seconds[-1].status_code}] {seconds[-1].message}")
        
        self.socket.send(f"AUTH LOGIN\r\n".encode('utf-8'))
        auth = self.parser.parse(self.socket.recv(1024))
        if auth.status_code != 334:
            raise SMTPConnectionError(f"【AUTH LOGIN】[{auth.status_code}] {auth.message}")
        self.socket.send(base64.b64encode(self.config.username.encode('utf-8')) + b'\r\n')
        auth = self.parser.parse(self.socket.recv(1024))
        if auth.status_code != 334:
            raise SMTPConnectionError(f"【AUTH LOGIN】[{auth.status_code}] {auth.message}")
        self.socket.send(base64.b64encode(self.config.password.encode('utf-8')) + b'\r\n')
        auth = self.parser.parse(self.socket.recv(1024))
        if auth.status_code == 535:
            raise SMTPInvalidCredentialError(f"Incorrect username or password")
        if auth.status_code != 235:
            raise SMTPConnectionError(f"【AUTH LOGIN】[{auth.status_code}] {auth.message}")
        
        for to in self.content.to:
            logger.info(f"Sending email to {to.name}<{to.address}>...")
            self.socket.send(f"MAIL FROM: <{self.content.sendmailname}>\r\n".encode('utf-8'))
            # This comes from qq mail itself, so it is definately a valid mail address.
            sending = self.parser.parse(self.socket.recv(1024))
            if sending.status_code == 501:
                raise SMTPInvalidMailError(f"Mail is not the same as the login account")
            if sending.status_code != 250:
                raise SMTPConnectionError(f"【MAIL FROM】[{sending.status_code}] {sending.message}")
            
            self.socket.send(f"RCPT TO: <{to.address}>\r\n".encode('utf-8'))
            sending = self.parser.parse(self.socket.recv(1024))
            if sending.status_code == 502:
                raise SMTPInvalidMailError(f"Mail {to.address} is not valid")  # though we have already verified it, just in case
            if sending.status_code != 250:
                raise SMTPConnectionError(f"【RCPT TO】[{sending.status_code}] {sending.message}")
            
            self.socket.send(f"DATA\r\n".encode('utf-8'))
            sending = self.parser.parse(self.socket.recv(1024))
            if sending.status_code != 354:
                raise SMTPConnectionError(f"【DATA】[{sending.status_code}] {sending.message}")
            
            self.socket.send(f"From: {self.content.sendmailname}\r\n".encode('utf-8'))
            self.socket.send(f'To: "{to.name}" <{to.address}>\r\n'.encode('utf-8'))
            self.socket.send(f"Subject: {self.content.subject}\r\n".encode('utf-8'))
            self.socket.send(f"Content-Type: text/html; charset=UTF-8\r\n".encode('utf-8'))
            self.socket.send(f".\r\n".encode('utf-8'))

            response = self.parser.parse(self.socket.recv(1024))
            if response.status_code == 500:
                raise SMTPMailNotExistsError(f"Mail {to.address} is not exist")
            if response.status_code != 250:
                raise SMTPConnectionError(f"【DATA】[{response.status_code}] {response.message}")
        
        self.socket.send(f"QUIT\r\n".encode('utf-8'))
        response = self.parser.parse(self.socket.recv(1024))
        if response.status_code != 221:
            raise SMTPConnectionError(f"【QUIT】[{response.status_code}] {response.message}")
        logger.success(f"Email \"{self.content.subject}\"[{len(self.content.content)}] from <{self.content.sendmailname}> to {to.name}<{to.address}> send successfully! "
                       f"From {self.server_socket.getpeername()[0]}:{self.server_socket.getpeername()[1]} to {self.config.smtp_server}:{self.config.smtp_port}")
        self.socket.close()
        self.server_socket.send(b"HTTP/1.1 200 OK\r\n\r\n")
        self.server_socket.close()





class SMTPForwarderFactory:
    def __init__(self):
        self.__queqe: queue.Queue[BaseSMTPForwarder] = queue.Queue()
        self.__thread = threading.Thread(target=self.__sender_queqe)
        self.__condition = threading.Condition()
        
        self.__thread.start()
        

    def add_forwarder(self, data: MailPostModel, *, parser: Type[SMTPParser] = SMTPParser):
        # Email address validation
        if isinstance(data, QQMailPostModel):
            self.__queqe.put(QQMailSMTPForwarder(data, parser=parser))
        else:
            raise ValueError(f"Invalid MailPostModel {type(data)}")
        with self.__condition:
            self.__condition.notify()

    def __sender_queqe(self):
        while True:
            with self.__condition:
                while self.__queqe.empty():
                    self.__condition.wait()
                
                
                email = self.__queqe.get()
            try:
                email.send()
            except SMTPConnectionError as e:
                logger.error(f"Connection error when sending email {email.content.subject}: {e}")
                email.server_socket.send(b"HTTP/1.1 500 Connection error\r\n\r\n")
            except SMTPInvalidCredentialError as e:
                logger.error(f'Error when sending email {email.content.subject}: {e}')
                email.server_socket.send(b"HTTP/1.1 403 Incorrect username or password\r\n\r\n")
            except SMTPInvalidMailError as e:
                logger.error(f'Error when sending email {email.content.subject}: {e}')
                email.server_socket.send(b"HTTP/1.1 403 Mail is not the same as the login account\r\n\r\n")
            except SMTPMailNotExistsError as e:
                logger.error(f'Error when sending email {email.content.subject}: {e}')
                email.server_socket.send(b"HTTP/1.1 403 Mail is not exist\r\n\r\n")
            finally:
                if email.socket:
                    email.socket.close()
                email.server_socket.close()
    

smtp_forwarder_factory: SMTPForwarderFactory = None

def get_smtp_forwarder() -> SMTPForwarderFactory:
    global smtp_forwarder_factory
    if smtp_forwarder_factory is None:
        smtp_forwarder_factory = SMTPForwarderFactory()
    return smtp_forwarder_factory
