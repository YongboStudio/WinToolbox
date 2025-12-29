"""选项卡基类"""

import tkinter as tk
from tkinter import ttk
from abc import ABC, abstractmethod


class BaseTab(ABC):
    """选项卡基类"""
    
    def __init__(self, parent: ttk.Notebook, is_admin: bool, lazy_load: bool = True):
        self.frame = ttk.Frame(parent)
        self.is_admin = is_admin
        self._loaded = False
        self._lazy_load = lazy_load
        
        if not lazy_load:
            self._do_load()
    
    def _do_load(self) -> None:
        """执行加载"""
        if not self._loaded:
            self.setup_ui()
            self._loaded = True
    
    def ensure_loaded(self) -> None:
        """确保已加载（用于懒加载触发）"""
        self._do_load()
    
    @property
    def is_loaded(self) -> bool:
        """是否已加载"""
        return self._loaded
    
    @abstractmethod
    def setup_ui(self) -> None:
        """设置 UI 界面"""
        pass
    
    def require_admin(self, action: str) -> bool:
        """检查管理员权限"""
        if not self.is_admin:
            from tkinter import messagebox
            messagebox.showwarning("警告", f"需要管理员权限才能{action}")
            return False
        return True
