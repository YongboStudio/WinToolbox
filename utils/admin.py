"""管理员权限相关工具"""

import ctypes
import sys


def set_taskbar_icon() -> None:
    """设置任务栏图标，使其显示自定义图标而非 Python 默认图标"""
    try:
        app_id = "WinToolbox.Toolbox.1.0"
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(app_id)
    except Exception:
        pass


def is_admin() -> bool:
    """检查是否以管理员权限运行"""
    try:
        return bool(ctypes.windll.shell32.IsUserAnAdmin())
    except Exception:
        return False


def run_as_admin() -> None:
    """以管理员权限重新启动程序"""
    if not is_admin():
        ctypes.windll.shell32.ShellExecuteW(
            None, "runas", sys.executable, " ".join(sys.argv), None, 1
        )
        sys.exit()
