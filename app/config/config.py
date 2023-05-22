from typing import Any, Union
from pathlib import Path
from pydantic import BaseSettings


class Config(BaseSettings):
    host: str = '0.0.0.0'
    port: int = 11567
    

    # Log
    log_level: str = 'INFO'
    log_save_path: Union[str, Path] = 'logs'


    # QQ SMTP
    QQ_MAIL_POST_URL: str = '/cgi-bin/compose_send'
    QQ_MAIL_WEBSERVER: str = 'mail.qq.com'
    
    
    class Config:
        env_file = '.env'


def get_config(**kwargs: Any) -> Config:
    """
    用于获取配置，可以通过传入参数来覆盖默认配置。
    """
    global config
    if config is None or kwargs:
        config = Config(**kwargs)
    return config


config: Config = None
