"""日志模块"""

import json
import os
import sys

from loguru import logger


def _get_logs_dir() -> str:
    """获取日志目录（避免循环导入，直接读取配置文件）"""
    config_file = os.path.join(os.path.expanduser("~"), ".wintoolbox", "settings.json")
    default_dir = os.path.join(os.path.expanduser("~"), ".wintoolbox", "logs")

    try:
        if os.path.exists(config_file):
            with open(config_file, encoding="utf-8") as f:
                data = json.load(f)
                logs_dir = data.get("logs_dir", "")
                if logs_dir:
                    return logs_dir
    except Exception:
        pass

    return default_dir


# 日志目录
LOG_DIR = _get_logs_dir()
os.makedirs(LOG_DIR, exist_ok=True)

# 移除默认处理器
logger.remove()

# 日志格式
LOG_FORMAT = "{time:YYYY-MM-DD HH:mm:ss} | {level:<8} | {name}:{function}:{line} | {message}"

# 文件日志（始终启用）
logger.add(
    os.path.join(LOG_DIR, "{time:YYYY-MM-DD}.log"),
    format=LOG_FORMAT,
    level="DEBUG",
    rotation="00:00",
    retention="30 days",
    encoding="utf-8"
)

# 终端日志处理器 ID
_console_handler_id = None


def enable_console_log() -> None:
    """启用终端日志输出"""
    global _console_handler_id
    if _console_handler_id is None:
        _console_handler_id = logger.add(
            sys.stdout,
            format=LOG_FORMAT,
            level="DEBUG",
            colorize=True
        )
        logger.info("终端日志输出已启用")


def disable_console_log() -> None:
    """禁用终端日志输出"""
    global _console_handler_id
    if _console_handler_id is not None:
        logger.info("终端日志输出已禁用")
        logger.remove(_console_handler_id)
        _console_handler_id = None


def is_console_log_enabled() -> bool:
    """检查终端日志是否启用"""
    return _console_handler_id is not None


# 导出 logger 实例
__all__ = ["logger", "enable_console_log", "disable_console_log", "is_console_log_enabled"]
