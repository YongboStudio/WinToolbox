"""Sysinternals Suite 管理选项卡"""

import os
import subprocess
import tkinter as tk
import webbrowser
from tkinter import messagebox, ttk

from services.tools import ToolsService
from utils.logger import logger

from .base import BaseTab

# Sysinternals 工具列表
SYSINTERNALS_TOOLS = [
    ("procmon.exe", "Process Monitor", "进程监控，实时监控文件系统、注册表和进程活动"),
    ("procexp.exe", "Process Explorer", "增强版任务管理器，查看进程详细信息"),
    ("autoruns.exe", "Autoruns", "管理系统启动项，查看所有自启动程序"),
    ("tcpview.exe", "TCPView", "网络连接查看器，显示所有TCP/UDP端点"),
    ("psexec.exe", "PsExec", "远程执行工具，在远程系统上执行进程"),
    ("handle.exe", "Handle", "查看进程打开的句柄"),
    ("listdlls.exe", "ListDLLs", "列出进程加载的DLL"),
    ("diskmon.exe", "DiskMon", "磁盘活动监控"),
    ("portmon.exe", "Portmon", "串口和并口监控"),
    ("dbgview.exe", "DebugView", "调试输出查看器"),
    ("accesschk.exe", "AccessChk", "权限检查工具"),
    ("adexplorer.exe", "AD Explorer", "Active Directory 浏览器"),
    ("bginfo.exe", "BgInfo", "桌面背景信息显示"),
    ("Coreinfo.exe", "Coreinfo", "CPU 和内存信息"),
    ("desktops.exe", "Desktops", "虚拟桌面管理"),
    ("disk2vhd.exe", "Disk2vhd", "磁盘转VHD工具"),
    ("du.exe", "Du", "磁盘使用统计"),
    ("hex2dec.exe", "Hex2dec", "进制转换工具"),
    ("junction.exe", "Junction", "目录链接管理"),
    ("livekd.exe", "LiveKd", "本地内核调试"),
    ("logonsessions.exe", "LogonSessions", "登录会话查看"),
    ("notmyfault.exe", "NotMyFault", "系统崩溃测试"),
    ("pendmoves.exe", "PendMoves", "待处理文件操作"),
    ("pipelist.exe", "PipeList", "命名管道列表"),
    ("procdump.exe", "ProcDump", "进程转储工具"),
    ("psgetsid.exe", "PsGetSid", "SID 查看工具"),
    ("psinfo.exe", "PsInfo", "系统信息"),
    ("pskill.exe", "PsKill", "进程终止工具"),
    ("pslist.exe", "PsList", "进程列表"),
    ("psloggedon.exe", "PsLoggedOn", "登录用户查看"),
    ("pspasswd.exe", "PsPasswd", "密码修改工具"),
    ("psservice.exe", "PsService", "服务管理"),
    ("psshutdown.exe", "PsShutdown", "关机工具"),
    ("pssuspend.exe", "PsSuspend", "进程挂起"),
    ("RAMMap.exe", "RAMMap", "内存分析工具"),
    ("RegDelNull.exe", "RegDelNull", "注册表空键删除"),
    ("regjump.exe", "RegJump", "注册表跳转"),
    ("ru.exe", "Registry Usage", "注册表使用统计"),
    ("sdelete.exe", "SDelete", "安全删除工具"),
    ("ShareEnum.exe", "ShareEnum", "共享枚举"),
    ("shellrunas.exe", "ShellRunas", "以其他用户运行"),
    ("sigcheck.exe", "Sigcheck", "文件签名检查"),
    ("streams.exe", "Streams", "NTFS流查看"),
    ("strings.exe", "Strings", "字符串提取"),
    ("sync.exe", "Sync", "磁盘同步"),
    ("Testlimit.exe", "Testlimit", "系统限制测试"),
    ("vmmap.exe", "VMMap", "虚拟内存分析"),
    ("volumeid.exe", "VolumeId", "卷ID修改"),
    ("whois.exe", "Whois", "域名查询"),
    ("Winobj.exe", "WinObj", "对象管理器查看"),
    ("ZoomIt.exe", "ZoomIt", "屏幕缩放和标注"),
]


class SysinternalsTab(BaseTab):
    """Sysinternals Suite 管理选项卡"""

    TOOL_ID = "sysinternals"

    def setup_ui(self) -> None:
        """设置 UI 界面"""
        # 标题
        header = ttk.Frame(self.frame)
        header.pack(fill=tk.X, padx=10, pady=10)

        ttk.Label(
            header,
            text="Sysinternals Suite",
            font=("Microsoft YaHei UI", 16, "bold")
        ).pack(side=tk.LEFT)

        # 主页链接
        homepage_link = ttk.Label(
            header,
            text="访问官网",
            foreground="blue",
            cursor="hand2"
        )
        homepage_link.pack(side=tk.RIGHT, padx=10)
        homepage_link.bind("<Button-1>", lambda e: webbrowser.open(
            "https://learn.microsoft.com/zh-cn/sysinternals/"
        ))

        # 状态和操作
        self._create_status_bar()

        # 工具列表
        self._create_tools_list()

        # 底部提示
        tip_frame = ttk.Frame(self.frame)
        tip_frame.pack(fill=tk.X, padx=10, pady=5)
        ttk.Label(
            tip_frame,
            text="💡 双击工具启动，部分工具需要管理员权限",
            foreground="gray"
        ).pack(side=tk.LEFT)

        # 刷新状态
        self._refresh_status()

    def _create_status_bar(self) -> None:
        """创建状态栏"""
        status_frame = ttk.Frame(self.frame)
        status_frame.pack(fill=tk.X, padx=10, pady=5)

        self.status_label = ttk.Label(status_frame, text="")
        self.status_label.pack(side=tk.LEFT)

        btn_frame = ttk.Frame(status_frame)
        btn_frame.pack(side=tk.RIGHT)

        self.install_btn = ttk.Button(
            btn_frame,
            text="下载安装",
            command=self._install_suite
        )
        self.install_btn.pack(side=tk.LEFT, padx=2)

        ttk.Button(
            btn_frame,
            text="打开目录",
            command=self._open_folder
        ).pack(side=tk.LEFT, padx=2)

        ttk.Button(
            btn_frame,
            text="刷新",
            command=self._refresh_status
        ).pack(side=tk.LEFT, padx=2)

    def _create_tools_list(self) -> None:
        """创建工具列表"""
        list_frame = ttk.LabelFrame(self.frame, text="工具列表")
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # 搜索框
        search_frame = ttk.Frame(list_frame)
        search_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Label(search_frame, text="搜索:").pack(side=tk.LEFT, padx=5)
        self.search_var = tk.StringVar()
        self.search_var.trace("w", lambda *args: self._filter_tools())
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var, width=30)
        search_entry.pack(side=tk.LEFT, padx=5)

        # 工具列表
        columns = ("exe", "name", "description", "status")
        self.tools_tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=15)

        self.tools_tree.heading("exe", text="文件名")
        self.tools_tree.heading("name", text="工具名称")
        self.tools_tree.heading("description", text="描述")
        self.tools_tree.heading("status", text="状态")

        self.tools_tree.column("exe", width=120)
        self.tools_tree.column("name", width=130)
        self.tools_tree.column("description", width=350)
        self.tools_tree.column("status", width=60)

        # 滚动条
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.tools_tree.yview)
        self.tools_tree.configure(yscrollcommand=scrollbar.set)

        self.tools_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=5)

        # 双击启动
        self.tools_tree.bind("<Double-1>", self._on_tool_double_click)

    def _refresh_status(self) -> None:
        """刷新状态"""
        tool = ToolsService.get_tool(self.TOOL_ID)
        if tool and tool.is_installed():
            self.status_label.config(text="✓ 已安装", foreground="green")
            self.install_btn.config(text="更新")
        else:
            self.status_label.config(text="✗ 未安装", foreground="red")
            self.install_btn.config(text="下载安装")

        self._load_tools()

    def _load_tools(self) -> None:
        """加载工具列表"""
        for item in self.tools_tree.get_children():
            self.tools_tree.delete(item)

        tool = ToolsService.get_tool(self.TOOL_ID)
        install_dir = tool.install_dir if tool else ""

        for exe, name, desc in SYSINTERNALS_TOOLS:
            exe_path = os.path.join(install_dir, exe) if install_dir else ""
            status = "✓" if exe_path and os.path.exists(exe_path) else "✗"
            self.tools_tree.insert("", tk.END, values=(exe, name, desc, status))

    def _filter_tools(self) -> None:
        """过滤工具列表"""
        keyword = self.search_var.get().lower()

        for item in self.tools_tree.get_children():
            self.tools_tree.delete(item)

        tool = ToolsService.get_tool(self.TOOL_ID)
        install_dir = tool.install_dir if tool else ""

        for exe, name, desc in SYSINTERNALS_TOOLS:
            if keyword and keyword not in exe.lower() and keyword not in name.lower() and keyword not in desc.lower():
                continue

            exe_path = os.path.join(install_dir, exe) if install_dir else ""
            status = "✓" if exe_path and os.path.exists(exe_path) else "✗"
            self.tools_tree.insert("", tk.END, values=(exe, name, desc, status))

    def _on_tool_double_click(self, event) -> None:
        """双击启动工具"""
        selected = self.tools_tree.selection()
        if not selected:
            return

        item = self.tools_tree.item(selected[0])
        exe_name = item["values"][0]
        tool_name = item["values"][1]

        tool = ToolsService.get_tool(self.TOOL_ID)
        if not tool or not tool.is_installed():
            messagebox.showwarning("警告", "请先下载安装 Sysinternals Suite")
            return

        exe_path = os.path.join(tool.install_dir, exe_name)
        if not os.path.exists(exe_path):
            messagebox.showerror("错误", f"工具文件不存在: {exe_name}")
            return

        try:
            logger.info(f"启动 Sysinternals 工具: {tool_name} ({exe_path})")
            subprocess.Popen([exe_path], creationflags=subprocess.CREATE_NO_WINDOW)
        except Exception as e:
            logger.error(f"启动工具失败: {tool_name}, 错误: {e}")
            messagebox.showerror("错误", f"启动失败: {e}")

    def _install_suite(self) -> None:
        """安装/更新套件"""
        import threading

        tool = ToolsService.get_tool(self.TOOL_ID)
        if not tool:
            return

        action = "更新" if tool.is_installed() else "下载"

        # 创建进度窗口
        progress_win = tk.Toplevel(self.frame)
        progress_win.title(f"{action} Sysinternals Suite")
        progress_win.geometry("350x120")
        progress_win.resizable(False, False)
        progress_win.transient(self.frame.winfo_toplevel())
        progress_win.grab_set()

        ttk.Label(progress_win, text=f"正在{action} Sysinternals Suite...").pack(pady=15)
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
            if tool.is_installed():
                ToolsService.uninstall(self.TOOL_ID)

            success, msg = ToolsService.download(self.TOOL_ID, update_progress)
            progress_win.destroy()

            if success:
                logger.info(f"Sysinternals Suite {action}成功")
                messagebox.showinfo("成功", f"Sysinternals Suite {action}完成")
            else:
                logger.error(f"Sysinternals Suite {action}失败: {msg}")
                messagebox.showerror("错误", msg)

            self._refresh_status()

        threading.Thread(target=download_thread, daemon=True).start()

    def _open_folder(self) -> None:
        """打开安装目录"""
        tool = ToolsService.get_tool(self.TOOL_ID)
        if tool and os.path.exists(tool.install_dir):
            os.startfile(tool.install_dir)
        else:
            messagebox.showinfo("提示", "请先下载安装 Sysinternals Suite")
