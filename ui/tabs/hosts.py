"""HOSTS 管理选项卡"""

import os
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from .base import BaseTab
from services.hosts import HostsService


class HostsTab(BaseTab):
    """HOSTS 管理选项卡"""
    
    def setup_ui(self) -> None:
        """设置 UI 界面"""
        self._create_buttons()
        self._create_add_entry()
        self._create_content_area()
        self.load_hosts()
    
    def _create_buttons(self) -> None:
        """创建按钮区域"""
        btn_frame = ttk.Frame(self.frame)
        btn_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(btn_frame, text="刷新", command=self.load_hosts).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="保存", command=self.save_hosts).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="打开文件位置", command=self._open_location).pack(side=tk.LEFT, padx=2)
    
    def _create_add_entry(self) -> None:
        """创建添加条目区域"""
        add_frame = ttk.LabelFrame(self.frame, text="添加条目")
        add_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(add_frame, text="IP:").pack(side=tk.LEFT, padx=2)
        self.ip_entry = ttk.Entry(add_frame, width=15)
        self.ip_entry.pack(side=tk.LEFT, padx=2)
        
        ttk.Label(add_frame, text="域名:").pack(side=tk.LEFT, padx=2)
        self.domain_entry = ttk.Entry(add_frame, width=30)
        self.domain_entry.pack(side=tk.LEFT, padx=2)
        
        ttk.Button(add_frame, text="添加", command=self._add_entry).pack(side=tk.LEFT, padx=5)
    
    def _create_content_area(self) -> None:
        """创建内容显示区域"""
        content_frame = ttk.LabelFrame(self.frame, text="HOSTS 文件内容")
        content_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.text = scrolledtext.ScrolledText(
            content_frame, wrap=tk.NONE, font=("Consolas", 10)
        )
        self.text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
    
    def load_hosts(self) -> None:
        """加载 HOSTS 文件"""
        try:
            content = HostsService.read()
            self.text.delete(1.0, tk.END)
            self.text.insert(tk.END, content)
        except Exception as e:
            messagebox.showerror("错误", f"读取 HOSTS 文件失败: {e}")
    
    def save_hosts(self) -> None:
        """保存 HOSTS 文件"""
        if not self.require_admin("修改 HOSTS 文件"):
            return
        
        try:
            content = self.text.get(1.0, tk.END)
            HostsService.write(content)
            messagebox.showinfo("成功", "HOSTS 文件已保存")
        except Exception as e:
            messagebox.showerror("错误", f"保存 HOSTS 文件失败: {e}")
    
    def _add_entry(self) -> None:
        """添加 HOSTS 条目"""
        ip = self.ip_entry.get().strip()
        domain = self.domain_entry.get().strip()
        
        if not ip or not domain:
            messagebox.showwarning("警告", "请输入 IP 和域名")
            return
        
        entry = HostsService.format_entry(ip, domain)
        self.text.insert(tk.END, entry)
        self.ip_entry.delete(0, tk.END)
        self.domain_entry.delete(0, tk.END)
    
    def _open_location(self) -> None:
        """打开 HOSTS 文件所在目录"""
        os.startfile(HostsService.get_directory())
