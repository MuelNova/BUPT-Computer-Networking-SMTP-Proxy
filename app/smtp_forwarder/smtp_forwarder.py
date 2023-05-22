import queue
import re
import threading
from abc import ABC, abstractmethod

from app.models import QQMailPostModel
from app.logging import logger

class BasicSMTPForwarder(ABC):
    ...
    @abstractmethod
    def send(self):
        raise NotImplementedError

class SMTPForwarder(BasicSMTPForwarder):
    ...

class QQMailSMTPForwarder(SMTPForwarder):
    ...

class SMTPForwarderFactory:
    def __init__(self):
        self.__queqe: queue.Queue[BasicSMTPForwarder] = queue.Queue()
        self.__thread = threading.Thread(target=self.__sender_queqe)
        self.__condition = threading.Condition()

        self.__thread.start()

    def add_forwarder(self, data: QQMailPostModel):
        # Email address validation
        
        return 
        self.__condition.notify()

    def __sender_queqe(self):
        while True:
            with self.__condition:
                while self.__queqe.empty():
                    self.__condition.wait()
                
                email = self.__queqe.get()
            
            email.send()

    def __del__(self):
        self.__thread.join()
    

smtp_forwarder_factory: SMTPForwarderFactory = None

def get_smtp_forwarder():
    global smtp_forwarder_factory
    if smtp_forwarder_factory is None:
        smtp_forwarder_factory = SMTPForwarderFactory()
    return smtp_forwarder_factory
