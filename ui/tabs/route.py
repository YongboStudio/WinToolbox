"""路由管理选项卡"""

import tkinter as tk
from tkinter import ttk, messagebox
from .base import BaseTab
from services.route import RouteService


class RouteTab(BaseTab):
    """路由管理选项卡"""
    
    def setup_ui(self) -> None:
        """设置 UI 界面"""
        self._create_buttons()
        self._create_add_route()
        self._create_route_table()
        self.load_routes()
    
    def _create_buttons(self) -> None:
        """创建按钮区域"""
        btn_frame = ttk.Frame(self.frame)
        btn_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(btn_frame, text="刷新路由表", command=self.load_routes).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="删除选中路由", command=self._delete_route).pack(side=tk.LEFT, padx=2)
    
    def _create_add_route(self) -> None:
        """创建添加路由区域"""
        add_frame = ttk.LabelFrame(self.frame, text="添加路由")
        add_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # 第一行
        row1 = ttk.Frame(add_frame)
        row1.pack(fill=tk.X, padx=5, pady=2)
        
        ttk.Label(row1, text="目标网络:").pack(side=tk.LEFT, padx=2)
        self.dest_entry = ttk.Entry(row1, width=15)
        self.dest_entry.pack(side=tk.LEFT, padx=2)
        
        ttk.Label(row1, text="子网掩码:").pack(side=tk.LEFT, padx=2)
        self.mask_entry = ttk.Entry(row1, width=15)
        self.mask_entry.pack(side=tk.LEFT, padx=2)
        self.mask_entry.insert(0, "255.255.255.0")
        
        ttk.Label(row1, text="网关:").pack(side=tk.LEFT, padx=2)
        self.gateway_entry = ttk.Entry(row1, width=15)
        self.gateway_entry.pack(side=tk.LEFT, padx=2)
        
        # 第二行
        row2 = ttk.Frame(add_frame)
        row2.pack(fill=tk.X, padx=5, pady=2)
        
        ttk.Label(row2, text="跃点数(可选):").pack(side=tk.LEFT, padx=2)
        self.metric_entry = ttk.Entry(row2, width=10)
        self.metric_entry.pack(side=tk.LEFT, padx=2)
        
        self.persistent_var = tk.BooleanVar()
        ttk.Checkbutton(row2, text="永久路由(-p)", variable=self.persistent_var).pack(side=tk.LEFT, padx=10)
        
        ttk.Button(row2, text="添加路由", command=self._add_route).pack(side=tk.LEFT, padx=10)
    
    def _create_route_table(self) -> None:
        """创建路由表显示区域"""
        table_frame = ttk.LabelFrame(self.frame, text="路由表")
        table_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        columns = ("dest", "mask", "gateway", "interface", "metric")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings")
        
        headings = [
            ("dest", "目标网络", 120),
            ("mask", "子网掩码", 120),
            ("gateway", "网关", 120),
            ("interface", "接口", 120),
            ("metric", "跃点数", 80),
        ]
        for col, text, width in headings:
            self.tree.heading(col, text=text)
            self.tree.column(col, width=width)
        
        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    def load_routes(self) -> None:
        """加载路由表"""
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        try:
            routes = RouteService.get_routes()
            for route in routes:
                self.tree.insert("", tk.END, values=(
                    route.destination, route.mask, route.gateway,
                    route.interface, route.metric
                ))
        except Exception as e:
            messagebox.showerror("错误", f"获取路由表失败: {e}")
    
    def _add_route(self) -> None:
        """添加路由"""
        if not self.require_admin("添加路由"):
            return
        
        dest = self.dest_entry.get().strip()
        mask = self.mask_entry.get().strip()
        gateway = self.gateway_entry.get().strip()
        metric = self.metric_entry.get().strip() or None
        persistent = self.persistent_var.get()
        
        if not dest or not mask or not gateway:
            messagebox.showwarning("警告", "请填写目标网络、子网掩码和网关")
            return
        
        try:
            success, message = RouteService.add(dest, mask, gateway, metric, persistent)
            if success:
                messagebox.showinfo("成功", message)
                self.load_routes()
            else:
                messagebox.showerror("错误", f"添加路由失败: {message}")
        except Exception as e:
            messagebox.showerror("错误", f"添加路由失败: {e}")
    
    def _delete_route(self) -> None:
        """删除选中的路由"""
        if not self.require_admin("删除路由"):
            return
        
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("警告", "请先选择要删除的路由")
            return
        
        item = self.tree.item(selected[0])
        dest = item["values"][0]
        
        if not messagebox.askyesno("确认", f"确定要删除目标为 {dest} 的路由吗?"):
            return
        
        try:
            success, message = RouteService.delete(dest)
            if success:
                messagebox.showinfo("成功", message)
                self.load_routes()
            else:
                messagebox.showerror("错误", f"删除路由失败: {message}")
        except Exception as e:
            messagebox.showerror("错误", f"删除路由失败: {e}")
