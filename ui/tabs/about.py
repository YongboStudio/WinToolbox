"""关于选项卡"""

import os
import subprocess
import sys
import tkinter as tk
import webbrowser
from tkinter import messagebox, ttk

from .base import BaseTab


class AboutTab(BaseTab):
    """关于选项卡"""

    # 项目信息
    APP_NAME = "Windows 系统工具箱"
    APP_VERSION = "1.0.0"
    AUTHOR = "YongboStudio"
    AUTHOR_URL = "https://github.com/YongboStudio"
    PROJECT_URL = "https://github.com/YongboStudio/WinToolbox"

    ABOUT_TEXT = """
        功能说明:
        ─────────────────────────────────────
        
        1. 快捷入口
           • 常用系统设置快捷方式
           • 第三方工具快捷启动
        
        2. HOSTS 管理
           • 查看和编辑 Windows HOSTS 文件
           • 快速添加 IP-域名 映射
        
        3. 路由管理
           • 查看当前路由表
           • 添加/删除路由 (支持永久路由)
        
        4. IP 地址
           • 查看所有网络适配器信息
           • 显示 IPv4、子网掩码、网关、DNS、MAC
        
        ─────────────────────────────────────
        
        注意事项:
        • 修改 HOSTS 和路由需要管理员权限
        • 请右键选择"以管理员身份运行"
    """

    def setup_ui(self) -> None:
        """设置 UI 界面"""
        self._create_header()
        self._create_about_text()
        self._create_links()
        self._create_shortcut_button()

    def _create_header(self) -> None:
        """创建头部信息"""
        header_frame = ttk.Frame(self.frame)
        header_frame.pack(fill=tk.X, padx=20, pady=15)

        # 应用名称和版本
        ttk.Label(
            header_frame,
            text=f"{self.APP_NAME}",
            font=("Microsoft YaHei UI", 16, "bold")
        ).pack()

        ttk.Label(
            header_frame,
            text=f"版本 {self.APP_VERSION}",
            foreground="gray"
        ).pack(pady=5)

    def _create_about_text(self) -> None:
        """创建关于文本"""
        text_widget = tk.Text(
            self.frame, wrap=tk.WORD, font=("Microsoft YaHei UI", 10), height=15
        )
        text_widget.pack(fill=tk.BOTH, expand=True, padx=20, pady=5)
        text_widget.insert(tk.END, self.ABOUT_TEXT)
        text_widget.config(state=tk.DISABLED)

    def _create_links(self) -> None:
        """创建链接区域"""
        links_frame = ttk.LabelFrame(self.frame, text="项目信息")
        links_frame.pack(fill=tk.X, padx=20, pady=10)

        # 作者信息
        row1 = ttk.Frame(links_frame)
        row1.pack(fill=tk.X, padx=10, pady=5)
        ttk.Label(row1, text="作者:").pack(side=tk.LEFT)
        author_link = ttk.Label(row1, text=self.AUTHOR, foreground="blue", cursor="hand2")
        author_link.pack(side=tk.LEFT, padx=5)
        author_link.bind("<Button-1>", lambda e: webbrowser.open(self.AUTHOR_URL))

        # 项目主页
        row2 = ttk.Frame(links_frame)
        row2.pack(fill=tk.X, padx=10, pady=5)
        ttk.Label(row2, text="项目主页:").pack(side=tk.LEFT)
        project_link = ttk.Label(row2, text=self.PROJECT_URL, foreground="blue", cursor="hand2")
        project_link.pack(side=tk.LEFT, padx=5)
        project_link.bind("<Button-1>", lambda e: webbrowser.open(self.PROJECT_URL))

    def _create_shortcut_button(self) -> None:
        """创建快捷方式按钮"""
        btn_frame = ttk.Frame(self.frame)
        btn_frame.pack(fill=tk.X, padx=20, pady=10)

        ttk.Button(
            btn_frame,
            text="创建桌面快捷方式",
            command=self._create_shortcut
        ).pack(side=tk.LEFT, padx=5)

        ttk.Label(
            btn_frame,
            text="提示: 创建快捷方式后可右键固定到任务栏",
            foreground="gray"
        ).pack(side=tk.LEFT, padx=10)

    def _create_shortcut(self) -> None:
        """创建桌面快捷方式"""
        try:
            import winreg

            # 获取桌面路径
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"Software\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders"
            )
            desktop_path = winreg.QueryValueEx(key, "Desktop")[0]
            winreg.CloseKey(key)

            # 创建 VBS 脚本
            script_path = os.path.join(os.environ["TEMP"], "create_shortcut.vbs")
            shortcut_path = os.path.join(desktop_path, "Windows系统工具箱.lnk")

            if getattr(sys, 'frozen', False):
                target_path = sys.executable
            else:
                target_path = os.path.abspath(sys.argv[0])

            vbs_content = f'''
Set WshShell = WScript.CreateObject("WScript.Shell")
Set shortcut = WshShell.CreateShortcut("{shortcut_path}")
shortcut.TargetPath = "{sys.executable}"
shortcut.Arguments = "{target_path}"
shortcut.WorkingDirectory = "{os.path.dirname(target_path)}"
shortcut.Description = "Windows 系统工具箱"
shortcut.Save
'''

            with open(script_path, "w", encoding="gbk") as f:
                f.write(vbs_content)

            subprocess.run(
                ["cscript", "//nologo", script_path],
                creationflags=subprocess.CREATE_NO_WINDOW
            )

            os.remove(script_path)

            messagebox.showinfo(
                "成功",
                "快捷方式已创建到桌面\n\n提示:\n"
                "1. 右键快捷方式 -> 属性 -> 高级\n"
                "2. 勾选'以管理员身份运行'\n"
                "3. 右键快捷方式 -> 固定到任务栏"
            )
        except Exception as e:
            messagebox.showerror("错误", f"创建快捷方式失败: {e}")
