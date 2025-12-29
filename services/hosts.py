"""HOSTS 文件服务"""

import os
from dataclasses import dataclass

from utils.logger import logger


@dataclass
class HostsEntry:
    """HOSTS 条目"""
    ip: str
    domain: str


class HostsService:
    """HOSTS 文件管理服务"""

    HOSTS_PATH = r"C:\Windows\System32\drivers\etc\hosts"

    @classmethod
    def get_path(cls) -> str:
        """获取 HOSTS 文件路径"""
        return cls.HOSTS_PATH

    @classmethod
    def get_directory(cls) -> str:
        """获取 HOSTS 文件所在目录"""
        return os.path.dirname(cls.HOSTS_PATH)

    @classmethod
    def read(cls) -> str:
        """读取 HOSTS 文件内容"""
        logger.debug(f"读取 HOSTS 文件: {cls.HOSTS_PATH}")
        with open(cls.HOSTS_PATH, encoding="utf-8") as f:
            return f.read()

    @classmethod
    def write(cls, content: str) -> None:
        """写入 HOSTS 文件内容"""
        logger.info(f"写入 HOSTS 文件: {cls.HOSTS_PATH}")
        with open(cls.HOSTS_PATH, "w", encoding="utf-8") as f:
            f.write(content)
        logger.info("HOSTS 文件保存成功")

    @staticmethod
    def format_entry(ip: str, domain: str) -> str:
        """格式化 HOSTS 条目"""
        return f"\n{ip}\t{domain}"
