import logging
from pathlib import Path
from datetime import datetime
from typing import Callable

from ..config import get_config

config = get_config()

SUCCESS = 25
logging.addLevelName(SUCCESS, "SUCCESS")
def success_wrap(self) -> Callable:
    def success(msg, *args, **kwargs):
        if self.isEnabledFor(SUCCESS):
            self._log(SUCCESS, msg, args, **kwargs)
    return success

log_level = config.log_level
log_save_path = config.log_save_path
if not Path(log_save_path).exists():
    Path(log_save_path).mkdir(parents=True)

log_format = logging.Formatter("\033[32m%(asctime)s \033[0m[%(levelname)s] \033[37m%(message)s\033[0m", "%H:%M:%S")
file_log_format = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s", "%H:%M:%S")

logger = logging.getLogger(__name__)
logger.success=success_wrap(logger)
logger.setLevel(log_level)
    
file_handler = logging.FileHandler(Path(log_save_path) / f'Log-{datetime.now().strftime("%Y%m%d%H%M")}.txt',
                                   encoding='utf-8')
file_handler.setLevel(log_level)
file_handler.setFormatter(file_log_format)
logger.addHandler(file_handler)


class ColoredFilter(logging.Filter):
    FMTDCIT = {
        'ERROR'   : "\033[31mERROR\033[0m",
        'INFO'    : "\033[37mINFO\033[0m",
        'DEBUG'   : "\033[34mDEBUG\033[0m",
        'WARN'    : "\033[33mWARN\033[0m",
        'WARNING' : "\033[33mWARNING\033[0m",
        'CRITICAL': "\033[35mCRITICAL\033[0m",
        'SUCCESS' : '\033[32mSUCCESS\033[0m'
    }
    COLOR_DICT = {
        'BLACK'  : "\033[30m",
        'RED'    : "\033[31m",
        'GREEN'  : "\033[32m",
        'YELLOW' : "\033[33m",
        'BLUE'   : "\033[34m",
        'PURPLE' : "\033[35m",
        'CYAN'   : "\033[36m",
        'WHITE'  : "\033[37m",
    }
    def filter(self, record: logging.LogRecord) -> bool:
        record.levelname = self.FMTDCIT.get(record.levelname)
        return True
stdout_handler = logging.StreamHandler()
stdout_handler.setLevel(log_level)
stdout_handler.setFormatter(log_format)
stdout_handler.addFilter(ColoredFilter())
logger.addHandler(stdout_handler)


__all__=['logger']