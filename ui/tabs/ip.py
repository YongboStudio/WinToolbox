"""IP 地址选项卡"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from .base import BaseTab
from services.network import NetworkService


class IPTab(BaseTab):
    """IP 地址选项卡"""
    
    def setup_ui(self) -> None:
        """设置 UI 界面"""
        self._create_buttons()
        self._create_adapter_table()
        self._create_detail_area()
        self.load_ip_info()
    
    def _create_buttons(self) -> None:
        """创建按钮区域"""
        btn_frame = ttk.Frame(self.frame)
        btn_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(btn_frame, text="刷新", command=self.load_ip_info).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="复制选中IP", command=self._copy_ip).pack(side=tk.LEFT, padx=2)
    
    def _create_adapter_table(self) -> None:
        """创建适配器信息表"""
        table_frame = ttk.LabelFrame(self.frame, text="网络适配器信息")
        table_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        columns = ("adapter", "ipv4", "mask", "gateway", "dns", "mac")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings")
        
        headings = [
            ("adapter", "适配器名称", 150),
            ("ipv4", "IPv4 地址", 120),
            ("mask", "子网掩码", 120),
            ("gateway", "默认网关", 120),
            ("dns", "DNS 服务器", 120),
            ("mac", "MAC 地址", 140),
        ]
        for col, text, width in headings:
            self.tree.heading(col, text=text)
            self.tree.column(col, width=width)
        
        v_scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.tree.yview)
        h_scrollbar = ttk.Scrollbar(table_frame, orient=tk.HORIZONTAL, command=self.tree.xview)
        self.tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        self.tree.grid(row=0, column=0, sticky="nsew")
        v_scrollbar.grid(row=0, column=1, sticky="ns")
        h_scrollbar.grid(row=1, column=0, sticky="ew")
        
        table_frame.grid_rowconfigure(0, weight=1)
        table_frame.grid_columnconfigure(0, weight=1)
    
    def _create_detail_area(self) -> None:
        """创建详细信息区域"""
        detail_frame = ttk.LabelFrame(self.frame, text="详细信息 (ipconfig /all)")
        detail_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.detail_text = scrolledtext.ScrolledText(
            detail_frame, wrap=tk.NONE, font=("Consolas", 9), height=10
        )
        self.detail_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
    
    def load_ip_info(self) -> None:
        """加载 IP 信息"""
        for item in self.tree.get_children():
            self.tree.delete(item)
        self.detail_text.delete(1.0, tk.END)
        
        try:
            # 获取详细输出
            output = NetworkService.get_ipconfig_output()
            self.detail_text.insert(tk.END, output)
            
            # 获取适配器列表
            adapters = NetworkService.get_adapters()
            for adapter in adapters:
                self.tree.insert("", tk.END, values=(
                    adapter.name, adapter.ipv4, adapter.mask,
                    adapter.gateway, adapter.dns, adapter.mac
                ))
        except Exception as e:
            messagebox.showerror("错误", f"获取 IP 信息失败: {e}")
    
    def _copy_ip(self) -> None:
        """复制选中的 IP 地址"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("警告", "请先选择一个网络适配器")
            return
        
        item = self.tree.item(selected[0])
        ip = item["values"][1]
        
        self.frame.clipboard_clear()
        self.frame.clipboard_append(ip)
        messagebox.showinfo("成功", f"已复制 IP 地址: {ip}")
