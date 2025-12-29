"""应用入口"""

import tkinter as tk

from services.settings import SettingsService
from ui import WinToolboxApp
from utils.admin import set_taskbar_icon
from utils.logger import enable_console_log, logger


def main() -> None:
    """主函数"""
    # 初始化日志
    settings = SettingsService.get()
    if settings.console_log:
        enable_console_log()

    logger.info("=" * 50)
    logger.info("Windows 系统工具箱启动")
    logger.info("=" * 50)

    # 设置任务栏图标（必须在创建窗口前调用）
    set_taskbar_icon()

    root = tk.Tk()
    WinToolboxApp(root)

    logger.info("主窗口已创建")
    root.mainloop()

    logger.info("应用程序退出")


if __name__ == "__main__":
    main()
