"""系统工具函数"""

import subprocess
from tkinter import messagebox


def run_command(
    cmd: list[str],
    shell: bool = False,
    encoding: str = "gbk"
) -> subprocess.CompletedProcess:
    """执行系统命令"""
    return subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        encoding=encoding,
        shell=shell,
        creationflags=subprocess.CREATE_NO_WINDOW
    )


def open_system_tool(cmd: list[str], name: str, shell: bool = False) -> None:
    """打开系统工具"""
    try:
        subprocess.Popen(
            cmd,
            shell=shell,
            creationflags=subprocess.CREATE_NO_WINDOW
        )
    except Exception as e:
        messagebox.showerror("错误", f"打开{name}失败: {e}")
