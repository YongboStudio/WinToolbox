"""主窗口"""

import os
import tkinter as tk
from tkinter import font, ttk

from services.settings import SettingsService
from utils.admin import is_admin, run_as_admin

from .tabs import AboutTab, HostsTab, IPTab, RouteTab, SettingsTab, ShortcutTab, SysinternalsTab


class WinToolboxApp:
    """Windows 系统工具箱主应用"""

    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Windows 系统工具箱")

        # 应用窗口尺寸设置
        settings = SettingsService.get()
        self.root.geometry(f"{settings.window_width}x{settings.window_height}")
        self.root.minsize(400, 300)

        self._is_admin = is_admin()

        self._set_icon()
        self._apply_font_settings()
        self._setup_ui()
        self._show_admin_status()

    def _set_icon(self) -> None:
        """设置窗口图标"""
        try:
            # 从 ui/ 目录向上一级找到项目根目录的 favicon.ico
            icon_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "favicon.ico")
            icon_path = os.path.abspath(icon_path)
            if os.path.exists(icon_path):
                self.root.iconbitmap(default=icon_path)
                self.root.wm_iconbitmap(icon_path)
        except Exception:
            pass

    def _apply_font_settings(self) -> None:
        """应用字体设置"""
        settings = SettingsService.get()
        size = settings.font_size

        # 设置默认字体
        default_font = font.nametofont("TkDefaultFont")
        default_font.configure(size=size)

        text_font = font.nametofont("TkTextFont")
        text_font.configure(size=size)

        fixed_font = font.nametofont("TkFixedFont")
        fixed_font.configure(size=size)

    def _setup_ui(self) -> None:
        """设置 UI 界面"""
        self._create_status_bar()
        self._create_notebook()

    def _create_status_bar(self) -> None:
        """创建状态栏"""
        status_frame = ttk.Frame(self.root)
        status_frame.pack(fill=tk.X, padx=5, pady=5)

        self.admin_label = ttk.Label(status_frame, text="")
        self.admin_label.pack(side=tk.LEFT)

        if not self._is_admin:
            admin_btn = ttk.Button(
                status_frame,
                text="以管理员身份重启",
                command=run_as_admin
            )
            admin_btn.pack(side=tk.RIGHT)

    def _create_notebook(self) -> None:
        """创建选项卡"""
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # 选项卡配置：(类, 标题, 是否懒加载)
        # 首页不懒加载，其他页面懒加载
        tab_configs = [
            (ShortcutTab, "快捷入口", False),  # 首页立即加载
            (HostsTab, "HOSTS 管理", True),
            (RouteTab, "路由管理", True),
            (IPTab, "IP 地址", True),
            (SysinternalsTab, "Sysinternals", True),
            (SettingsTab, "设置", True),
            (AboutTab, "关于", True),
        ]

        self._tabs = []
        for tab_class, title, lazy_load in tab_configs:
            tab = tab_class(self.notebook, self._is_admin, lazy_load=lazy_load)
            self.notebook.add(tab.frame, text=title)
            self._tabs.append(tab)

        # 绑定选项卡切换事件
        self.notebook.bind("<<NotebookTabChanged>>", self._on_tab_changed)

    def _on_tab_changed(self, event) -> None:
        """选项卡切换事件"""
        selected_index = self.notebook.index(self.notebook.select())
        if 0 <= selected_index < len(self._tabs):
            tab = self._tabs[selected_index]
            tab.ensure_loaded()

    def _show_admin_status(self) -> None:
        """显示管理员状态"""
        if self._is_admin:
            self.admin_label.config(
                text="✓ 已以管理员权限运行",
                foreground="green"
            )
        else:
            self.admin_label.config(
                text="⚠ 未以管理员权限运行 (部分功能受限)",
                foreground="red"
            )
