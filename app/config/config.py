from typing import Any, Union, Literal, List
from pathlib import Path
from pydantic import BaseSettings, validator, BaseModel, ValidationError

class AccountConfig(BaseModel):
    type: Literal['qq']
    username: str
    password: str
    smtp_server: str
    smtp_port: int

    class Config:
        validate_assignment = True


class Config(BaseSettings):
    # 配置监听端口等
    host: str = '0.0.0.0'
    port: int = 11567
    

    # Log
    log_level: str = 'INFO'
    log_save_path: Union[str, Path] = 'logs'


    # QQ SMTP
    QQ_MAIL_POST_URL: str = '/cgi-bin/compose_send'
    QQ_MAIL_WEBSERVER: str = 'mail.qq.com'

    accounts: List[AccountConfig] | str
    
    class Config:
        env_file = '.env'

    @validator('accounts', pre=True, always=True)
    def accounts_validator(cls, value: str) -> List['AccountConfig']:
        res = []
        value = value.split(' ')
        for i in value:
            if not isinstance(i, str):
                raise ValidationError(f'Invalid account type of {i}, expected str')
            i = i.split(';')
            if len(i) != 5:
                raise ValidationError('Invalid account format, expected "type;username;password;smtp_server;smtp_port"')
            res.append(AccountConfig(
                type=i[0],
                username=i[1],
                password=i[2],
                smtp_server=i[3],
                smtp_port=int(i[4])
            ))
        return res


def get_config(**kwargs: Any) -> Config:
    """
    用于获取配置，可以通过传入参数来覆盖默认配置。
    """
    global config
    if config is None or kwargs:
        config = Config(**kwargs)
    return config


config: Config = None
