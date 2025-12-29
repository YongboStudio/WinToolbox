"""关于选项卡"""

import os
import subprocess
import sys
import tkinter as tk
import webbrowser
from tkinter import messagebox, ttk

from .base import BaseTab


def get_base_path() -> str:
    """获取基础路径"""
    if getattr(sys, 'frozen', False):
        return sys._MEIPASS  # type: ignore
    return os.path.dirname(os.path.dirname(os.path.dirname(__file__)))


def get_build_time() -> str:
    """获取构建时间"""
    buildtime_file = os.path.join(get_base_path(), 'buildtime.txt')
    if os.path.exists(buildtime_file):
        with open(buildtime_file, encoding='utf-8') as f:
            return f.read().strip()
    return "开发模式"


def get_version() -> str:
    """从 pyproject.toml 读取版本号"""
    pyproject_file = os.path.join(get_base_path(), 'pyproject.toml')
    if os.path.exists(pyproject_file):
        with open(pyproject_file, encoding='utf-8') as f:
            import re
            content = f.read()
            match = re.search(r'version\s*=\s*"([^"]+)"', content)
            if match:
                return match.group(1)
    return "未知"


def get_features_from_readme() -> str:
    """从 README.md 读取功能特性"""
    readme_file = os.path.join(get_base_path(), 'README.md')
    if not os.path.exists(readme_file):
        return "功能特性信息不可用"
    
    with open(readme_file, encoding='utf-8') as f:
        content = f.read()
    
    # 提取 ## 功能特性 到下一个 ## 之间的内容
    import re
    match = re.search(r'## 功能特性\s*\n(.*?)(?=\n## |\Z)', content, re.DOTALL)
    if match:
        features = match.group(1).strip()
        # 简化格式：移除 ### 和 emoji
        features = re.sub(r'### [^\n]*\n', '', features)
        features = re.sub(r'^- ', '• ', features, flags=re.MULTILINE)
        return features
    return "功能特性信息不可用"


class AboutTab(BaseTab):
    """关于选项卡"""

    # 项目信息
    APP_NAME = "Windows 系统工具箱"
    AUTHOR = "YongboStudio"
    AUTHOR_URL = "https://github.com/YongboStudio"
    PROJECT_URL = "https://github.com/YongboStudio/WinToolbox"

    ABOUT_TEXT = ""  # 动态从 README 获取

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

        version = get_version()
        ttk.Label(
            header_frame,
            text=f"版本 {version}",
            foreground="gray"
        ).pack(pady=5)

        # 构建时间
        build_time = get_build_time()
        ttk.Label(
            header_frame,
            text=f"构建时间: {build_time}",
            foreground="gray"
        ).pack()

    def _create_about_text(self) -> None:
        """创建关于文本"""
        features = get_features_from_readme()
        
        text_widget = tk.Text(
            self.frame, wrap=tk.WORD, font=("Microsoft YaHei UI", 10), height=15
        )
        text_widget.pack(fill=tk.BOTH, expand=True, padx=20, pady=5)
        text_widget.insert(tk.END, features)
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
