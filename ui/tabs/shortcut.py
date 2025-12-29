"""快捷入口选项卡"""

import threading
import tkinter as tk
from tkinter import messagebox, ttk

from services.tools import ToolsService
from utils.system import open_system_tool

from .base import BaseTab


class ShortcutTab(BaseTab):
    """快捷入口选项卡"""

    def setup_ui(self) -> None:
        """设置 UI 界面"""
        # 标题
        title_label = ttk.Label(
            self.frame,
            text="Windows 系统快捷入口",
            font=("Microsoft YaHei UI", 16, "bold")
        )
        title_label.pack(pady=20)

        # 快捷方式容器
        container = ttk.Frame(self.frame)
        container.pack(fill=tk.BOTH, expand=True, padx=40, pady=10)

        # 创建快捷方式分类
        shortcuts = self._get_shortcuts()
        for i, category in enumerate(shortcuts):
            self._create_category(container, category, i)

        # 配置网格权重
        container.grid_columnconfigure(0, weight=1)
        container.grid_columnconfigure(1, weight=1)

        # 底部提示
        self._create_tip()

    def _get_shortcuts(self) -> list[dict]:
        """获取快捷方式配置"""
        return [
            {
                "category": "系统设置",
                "items": [
                    ("🌐 环境变量", "编辑系统和用户环境变量", self._open_env_variables),
                    ("📡 网络连接 (IP配置)", "配置网络适配器IP地址", self._open_network_connections),
                    ("🎛️ 传统控制面板", "打开经典控制面板", self._open_control_panel),
                ]
            },
            {
                "category": "网络工具",
                "items": [
                    ("🔧 网络适配器设置", "高级网络适配器选项", self._open_adapter_settings),
                    ("🛡️ Windows 防火墙", "配置防火墙规则", self._open_firewall),
                    ("📊 资源监视器", "查看网络资源使用", self._open_resmon),
                ]
            },
            {
                "category": "系统工具",
                "items": [
                    ("💻 设备管理器", "管理硬件设备", self._open_device_manager),
                    ("📋 服务管理", "管理Windows服务", self._open_services),
                    ("⚡ 任务管理器", "查看进程和性能", self._open_task_manager),
                ]
            },
            {
                "category": "第三方工具",
                "items": [
                    ("🗑️ 软件卸载 (Geek)", "高效卸载软件及残留", self._open_geek_uninstaller),
                    ("🔬 进程监控 (ProcMon)", "实时监控进程活动", self._open_sysinternals),
                    ("🌐 网络连接 (TCPView)", "查看所有TCP/UDP连接", self._open_tcpview),
                ]
            }
        ]

    def _create_category(self, parent: ttk.Frame, category: dict, index: int) -> None:
        """创建分类框架"""
        cat_frame = ttk.LabelFrame(parent, text=category["category"])
        cat_frame.grid(row=index // 2, column=index % 2, padx=10, pady=10, sticky="nsew")

        for name, desc, cmd in category["items"]:
            btn_frame = ttk.Frame(cat_frame)
            btn_frame.pack(fill=tk.X, padx=10, pady=5)

            btn = ttk.Button(btn_frame, text=name, width=25, command=cmd)
            btn.pack(side=tk.LEFT)

            desc_label = ttk.Label(btn_frame, text=desc, foreground="gray")
            desc_label.pack(side=tk.LEFT, padx=10)

    def _create_tip(self) -> None:
        """创建底部提示"""
        tip_frame = ttk.Frame(self.frame)
        tip_frame.pack(fill=tk.X, padx=20, pady=20)
        ttk.Label(
            tip_frame,
            text="💡 提示: 部分设置需要管理员权限才能修改",
            foreground="gray"
        ).pack()

    # 系统工具快捷方式
    def _open_env_variables(self) -> None:
        open_system_tool(["rundll32.exe", "sysdm.cpl,EditEnvironmentVariables"], "环境变量")

    def _open_network_connections(self) -> None:
        open_system_tool(["ncpa.cpl"], "网络连接", shell=True)

    def _open_control_panel(self) -> None:
        open_system_tool(["control"], "控制面板")

    def _open_adapter_settings(self) -> None:
        open_system_tool(["control", "ncpa.cpl"], "网络适配器设置")

    def _open_firewall(self) -> None:
        open_system_tool(["wf.msc"], "防火墙", shell=True)

    def _open_resmon(self) -> None:
        open_system_tool(["resmon"], "资源监视器")

    def _open_device_manager(self) -> None:
        open_system_tool(["devmgmt.msc"], "设备管理器", shell=True)

    def _open_services(self) -> None:
        open_system_tool(["services.msc"], "服务管理", shell=True)

    def _open_task_manager(self) -> None:
        open_system_tool(["taskmgr"], "任务管理器")

    # 第三方工具
    def _open_geek_uninstaller(self) -> None:
        """打开 Geek Uninstaller"""
        self._open_third_party_tool("geek_uninstaller")

    def _open_sysinternals(self) -> None:
        """打开 Sysinternals Process Monitor"""
        self._open_sysinternals_tool("procmon.exe", "Process Monitor")

    def _open_tcpview(self) -> None:
        """打开 TCPView 网络连接监控"""
        self._open_sysinternals_tool("tcpview.exe", "TCPView")

    def _open_sysinternals_tool(self, exe_name: str, tool_name: str) -> None:
        """打开 Sysinternals 工具"""
        import os
        import subprocess

        tool = ToolsService.get_tool("sysinternals")
        if not tool:
            return

        if not tool.is_installed():
            if messagebox.askyesno("下载确认", "Sysinternals Suite 尚未安装，是否立即下载？"):
                self._download_tool("sysinternals")
            return

        exe_path = os.path.join(tool.install_dir, exe_name)
        if not os.path.exists(exe_path):
            messagebox.showerror("错误", f"工具文件不存在: {exe_name}")
            return

        try:
            subprocess.Popen([exe_path], creationflags=subprocess.CREATE_NO_WINDOW)
        except Exception as e:
            messagebox.showerror("错误", f"启动 {tool_name} 失败: {e}")

    def _open_third_party_tool(self, tool_id: str) -> None:
        """打开第三方工具"""
        tool = ToolsService.get_tool(tool_id)
        if not tool:
            return

        if tool.is_installed():
            success, msg = ToolsService.launch(tool_id)
            if not success:
                messagebox.showerror("错误", msg)
        else:
            if messagebox.askyesno("下载确认", f"{tool.name} 尚未安装，是否立即下载？"):
                self._download_tool(tool_id)

    def _download_tool(self, tool_id: str) -> None:
        """下载工具"""
        tool = ToolsService.get_tool(tool_id)
        if not tool:
            return

        # 创建下载进度窗口
        progress_win = tk.Toplevel(self.frame)
        progress_win.title(f"下载 {tool.name}")
        progress_win.geometry("350x120")
        progress_win.resizable(False, False)
        progress_win.transient(self.frame.winfo_toplevel())
        progress_win.grab_set()

        ttk.Label(progress_win, text=f"正在下载 {tool.name}...").pack(pady=15)
        progress_bar = ttk.Progressbar(progress_win, length=300, mode="determinate")
        progress_bar.pack(pady=5)
        progress_label = ttk.Label(progress_win, text="0%")
        progress_label.pack(pady=10)

        def update_progress(downloaded: int, total: int):
            percent = int(downloaded * 100 / total)
            progress_bar["value"] = percent
            progress_label.config(text=f"{percent}%")
            progress_win.update()

        def download_thread():
            success, msg = ToolsService.download(tool_id, update_progress)
            progress_win.destroy()
            if success:
                messagebox.showinfo("成功", f"{tool.name} 下载完成")
                ToolsService.launch(tool_id)
            else:
                messagebox.showerror("错误", msg)

        threading.Thread(target=download_thread, daemon=True).start()
