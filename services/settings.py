"""设置服务"""

import json
import os
from dataclasses import asdict, dataclass


@dataclass
class AppSettings:
    """应用设置"""
    font_size: int = 10
    console_log: bool = False
    window_width: int = 900
    window_height: int = 650
    tools_dir: str = ""  # 空字符串表示使用默认目录
    logs_dir: str = ""   # 空字符串表示使用默认目录

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "AppSettings":
        return cls(
            font_size=data.get("font_size", 10),
            console_log=data.get("console_log", False),
            window_width=data.get("window_width", 900),
            window_height=data.get("window_height", 650),
            tools_dir=data.get("tools_dir", ""),
            logs_dir=data.get("logs_dir", "")
        )

    @staticmethod
    def get_default_tools_dir() -> str:
        """获取默认工具目录"""
        return os.path.join(os.path.expanduser("~"), ".wintoolbox", "tools")

    @staticmethod
    def get_default_logs_dir() -> str:
        """获取默认日志目录"""
        return os.path.join(os.path.expanduser("~"), ".wintoolbox", "logs")

    def get_tools_dir(self) -> str:
        """获取工具目录（如果未设置则返回默认值）"""
        return self.tools_dir if self.tools_dir else self.get_default_tools_dir()

    def get_logs_dir(self) -> str:
        """获取日志目录（如果未设置则返回默认值）"""
        return self.logs_dir if self.logs_dir else self.get_default_logs_dir()


class SettingsService:
    """设置服务"""

    _settings: AppSettings | None = None
    _config_dir = os.path.join(os.path.expanduser("~"), ".wintoolbox")
    _config_file = os.path.join(_config_dir, "settings.json")

    @classmethod
    def get(cls) -> AppSettings:
        """获取设置"""
        if cls._settings is None:
            cls._settings = cls._load()
        return cls._settings

    @classmethod
    def save(cls, settings: AppSettings) -> None:
        """保存设置"""
        cls._settings = settings
        os.makedirs(cls._config_dir, exist_ok=True)
        with open(cls._config_file, "w", encoding="utf-8") as f:
            json.dump(settings.to_dict(), f, indent=2)

    @classmethod
    def _load(cls) -> AppSettings:
        """加载设置"""
        try:
            if os.path.exists(cls._config_file):
                with open(cls._config_file, encoding="utf-8") as f:
                    data = json.load(f)
                return AppSettings.from_dict(data)
        except Exception:
            pass
        return AppSettings()
