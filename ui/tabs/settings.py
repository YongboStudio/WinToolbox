"""设置选项卡"""

import os
import threading
import tkinter as tk
from tkinter import messagebox, ttk

from services.settings import AppSettings, SettingsService
from services.tools import ToolsService
from utils.logger import disable_console_log, enable_console_log, logger

from .base import BaseTab


class SettingsTab(BaseTab):
    """设置选项卡"""

    def setup_ui(self) -> None:
        """设置 UI 界面"""
        self.settings = SettingsService.get()

        # 标题
        title_label = ttk.Label(
            self.frame,
            text="工具箱设置",
            font=("Microsoft YaHei UI", 16, "bold")
        )
        title_label.pack(pady=20)

        # 设置容器（可滚动）
        self.canvas = tk.Canvas(self.frame)
        scrollbar = ttk.Scrollbar(self.frame, orient="vertical", command=self.canvas.yview)
        self.container = ttk.Frame(self.canvas)

        self.container.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        canvas_frame = self.canvas.create_window((0, 0), window=self.container, anchor="nw")
        self.canvas.configure(yscrollcommand=scrollbar.set)

        # 绑定鼠标滚轮事件
        def _on_mousewheel(event):
            self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        def _bind_mousewheel(event):
            self.canvas.bind_all("<MouseWheel>", _on_mousewheel)

        def _unbind_mousewheel(event):
            self.canvas.unbind_all("<MouseWheel>")

        self.canvas.bind("<Enter>", _bind_mousewheel)
        self.canvas.bind("<Leave>", _unbind_mousewheel)

        # 让 container 宽度跟随 canvas
        def _configure_canvas(event):
            self.canvas.itemconfig(canvas_frame, width=event.width)

        self.canvas.bind("<Configure>", _configure_canvas)

        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=20)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self._create_display_settings()
        self._create_log_settings()
        self._create_tools_dir_settings()
        self._create_tools_management()
        self._create_buttons()

    def _create_display_settings(self) -> None:
        """创建显示设置"""
        frame = ttk.LabelFrame(self.container, text="显示设置")
        frame.pack(fill=tk.X, padx=10, pady=10)

        # 字体大小
        row1 = ttk.Frame(frame)
        row1.pack(fill=tk.X, padx=10, pady=5)

        ttk.Label(row1, text="字体大小:").pack(side=tk.LEFT, padx=5)

        self.font_size_var = tk.IntVar(value=self.settings.font_size)
        font_sizes = ["8", "9", "10", "11", "12", "14", "16", "18", "20"]

        self.font_size_combo = ttk.Combobox(
            row1,
            textvariable=self.font_size_var,
            values=font_sizes,
            width=10,
            state="readonly"
        )
        self.font_size_combo.pack(side=tk.LEFT, padx=5)

        ttk.Label(row1, text="(重启后生效)", foreground="gray").pack(side=tk.LEFT, padx=5)

        # 窗口尺寸
        row2 = ttk.Frame(frame)
        row2.pack(fill=tk.X, padx=10, pady=5)

        ttk.Label(row2, text="窗口宽度:").pack(side=tk.LEFT, padx=5)
        self.window_width_var = tk.StringVar(value=str(self.settings.window_width))
        width_entry = ttk.Entry(row2, textvariable=self.window_width_var, width=8)
        width_entry.pack(side=tk.LEFT, padx=5)

        ttk.Label(row2, text="窗口高度:").pack(side=tk.LEFT, padx=15)
        self.window_height_var = tk.StringVar(value=str(self.settings.window_height))
        height_entry = ttk.Entry(row2, textvariable=self.window_height_var, width=8)
        height_entry.pack(side=tk.LEFT, padx=5)

        ttk.Label(row2, text="(重启后生效)", foreground="gray").pack(side=tk.LEFT, padx=5)

    def _create_log_settings(self) -> None:
        """创建日志设置"""
        frame = ttk.LabelFrame(self.container, text="日志设置")
        frame.pack(fill=tk.X, padx=10, pady=10)

        # 终端日志开关
        row1 = ttk.Frame(frame)
        row1.pack(fill=tk.X, padx=10, pady=5)

        self.console_log_var = tk.BooleanVar(value=self.settings.console_log)
        ttk.Checkbutton(
            row1,
            text="输出日志到终端",
            variable=self.console_log_var,
            command=self._toggle_console_log
        ).pack(side=tk.LEFT, padx=5)

        # 日志目录
        row2 = ttk.Frame(frame)
        row2.pack(fill=tk.X, padx=10, pady=5)

        ttk.Label(row2, text="日志目录:").pack(side=tk.LEFT, padx=5)

        current_logs_dir = self.settings.get_logs_dir()
        self.logs_dir_var = tk.StringVar(value=current_logs_dir)
        logs_dir_entry = ttk.Entry(row2, textvariable=self.logs_dir_var, width=50)
        logs_dir_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)

        ttk.Button(row2, text="浏览", command=self._browse_logs_dir).pack(side=tk.LEFT, padx=5)
        ttk.Button(row2, text="打开", command=self._open_logs_dir).pack(side=tk.LEFT, padx=5)

        # 提示
        tip_row = ttk.Frame(frame)
        tip_row.pack(fill=tk.X, padx=10, pady=5)
        default_logs_dir = AppSettings.get_default_logs_dir()
        ttk.Label(tip_row, text=f"默认: {default_logs_dir} (重启后生效)", foreground="gray").pack(side=tk.LEFT)

    def _browse_logs_dir(self) -> None:
        """浏览选择日志目录"""
        from tkinter import filedialog
        dir_path = filedialog.askdirectory(
            title="选择日志保存目录",
            initialdir=self.logs_dir_var.get()
        )
        if dir_path:
            self.logs_dir_var.set(dir_path)

    def _open_logs_dir(self) -> None:
        """打开日志目录"""
        import subprocess
        dir_path = self.logs_dir_var.get()
        if os.path.exists(dir_path):
            subprocess.Popen(["explorer", dir_path])
        else:
            if messagebox.askyesno("提示", f"目录不存在，是否创建？\n{dir_path}"):
                os.makedirs(dir_path, exist_ok=True)
                subprocess.Popen(["explorer", dir_path])

    def _create_tools_dir_settings(self) -> None:
        """创建工具目录设置"""
        frame = ttk.LabelFrame(self.container, text="工具目录设置")
        frame.pack(fill=tk.X, padx=10, pady=10)

        row = ttk.Frame(frame)
        row.pack(fill=tk.X, padx=10, pady=10)

        ttk.Label(row, text="安装目录:").pack(side=tk.LEFT, padx=5)

        current_dir = self.settings.get_tools_dir()
        self.tools_dir_var = tk.StringVar(value=current_dir)
        tools_dir_entry = ttk.Entry(row, textvariable=self.tools_dir_var, width=50)
        tools_dir_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)

        ttk.Button(row, text="浏览", command=self._browse_tools_dir).pack(side=tk.LEFT, padx=5)
        ttk.Button(row, text="打开", command=self._open_tools_dir).pack(side=tk.LEFT, padx=5)

        # 提示
        tip_row = ttk.Frame(frame)
        tip_row.pack(fill=tk.X, padx=10, pady=5)
        default_dir = AppSettings.get_default_tools_dir()
        ttk.Label(tip_row, text=f"默认: {default_dir}", foreground="gray").pack(side=tk.LEFT)

    def _browse_tools_dir(self) -> None:
        """浏览选择工具目录"""
        from tkinter import filedialog
        dir_path = filedialog.askdirectory(
            title="选择工具安装目录",
            initialdir=self.tools_dir_var.get()
        )
        if dir_path:
            self.tools_dir_var.set(dir_path)

    def _open_tools_dir(self) -> None:
        """打开工具目录"""
        import subprocess
        dir_path = self.tools_dir_var.get()
        if os.path.exists(dir_path):
            subprocess.Popen(["explorer", dir_path])
        else:
            if messagebox.askyesno("提示", f"目录不存在，是否创建？\n{dir_path}"):
                os.makedirs(dir_path, exist_ok=True)
                subprocess.Popen(["explorer", dir_path])

    def _toggle_console_log(self) -> None:
        """切换终端日志"""
        if self.console_log_var.get():
            enable_console_log()
            logger.info("用户启用终端日志输出")
        else:
            logger.info("用户禁用终端日志输出")
            disable_console_log()

    def _create_tools_management(self) -> None:
        """创建第三方工具管理"""

        tools_frame = ttk.LabelFrame(self.container, text="第三方工具管理")
        tools_frame.pack(fill=tk.X, padx=10, pady=10)

        # 工具列表
        columns = ("name", "status", "description")
        self.tools_tree = ttk.Treeview(tools_frame, columns=columns, show="headings", height=5)

        self.tools_tree.heading("name", text="工具名称")
        self.tools_tree.heading("status", text="状态")
        self.tools_tree.heading("description", text="描述")

        self.tools_tree.column("name", width=150)
        self.tools_tree.column("status", width=80)
        self.tools_tree.column("description", width=250)

        self.tools_tree.pack(fill=tk.X, padx=10, pady=5)
        self.tools_tree.bind("<<TreeviewSelect>>", self._on_tool_selected)

        # 按钮区域
        btn_frame = ttk.Frame(tools_frame)
        btn_frame.pack(fill=tk.X, padx=10, pady=5)

        ttk.Button(btn_frame, text="刷新", command=self._refresh_tools).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="下载/更新", command=self._download_selected_tool).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="卸载", command=self._uninstall_selected_tool).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="编辑", command=self._edit_selected_tool).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="访问主页", command=self._open_tool_homepage).pack(side=tk.LEFT, padx=2)

        # 加载工具列表
        self._refresh_tools()

    def _on_tool_selected(self, event) -> None:
        """工具选中事件"""
        pass

    def _open_tool_homepage(self) -> None:
        """打开工具主页"""
        import webbrowser

        selected = self.tools_tree.selection()
        if not selected:
            messagebox.showwarning("警告", "请先选择一个工具")
            return

        tool_id = selected[0]
        tool = ToolsService.get_tool(tool_id)
        if tool and tool.homepage:
            webbrowser.open(tool.homepage)
        else:
            messagebox.showinfo("提示", "该工具未设置主页")

    def _edit_selected_tool(self) -> None:
        """编辑选中的工具"""
        selected = self.tools_tree.selection()
        if not selected:
            messagebox.showwarning("警告", "请先选择一个工具")
            return

        tool_id = selected[0]
        tool = ToolsService.get_tool(tool_id)
        if not tool:
            return

        # 创建编辑窗口
        edit_win = tk.Toplevel(self.frame)
        edit_win.title(f"编辑 {tool.name}")
        edit_win.geometry("500x200")
        edit_win.resizable(False, False)
        edit_win.transient(self.frame.winfo_toplevel())
        edit_win.grab_set()

        # 工具名称（只读）
        row1 = ttk.Frame(edit_win)
        row1.pack(fill=tk.X, padx=15, pady=10)
        ttk.Label(row1, text="工具名称:", width=12).pack(side=tk.LEFT)
        ttk.Label(row1, text=tool.name).pack(side=tk.LEFT, padx=5)

        # 下载地址
        row2 = ttk.Frame(edit_win)
        row2.pack(fill=tk.X, padx=15, pady=5)
        ttk.Label(row2, text="下载地址:", width=12).pack(side=tk.LEFT)
        url_var = tk.StringVar(value=tool.download_url)
        url_entry = ttk.Entry(row2, textvariable=url_var, width=50)
        url_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)

        # 主页地址
        row3 = ttk.Frame(edit_win)
        row3.pack(fill=tk.X, padx=15, pady=5)
        ttk.Label(row3, text="主页地址:", width=12).pack(side=tk.LEFT)
        homepage_var = tk.StringVar(value=tool.homepage)
        homepage_entry = ttk.Entry(row3, textvariable=homepage_var, width=50)
        homepage_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)

        # 按钮
        btn_frame = ttk.Frame(edit_win)
        btn_frame.pack(fill=tk.X, padx=15, pady=20)

        def save_changes():
            new_url = url_var.get().strip()
            new_homepage = homepage_var.get().strip()

            if new_url:
                ToolsService.update_tool_url(tool_id, new_url)
            if new_homepage != tool.homepage:
                ToolsService.update_tool_homepage(tool_id, new_homepage)

            messagebox.showinfo("成功", "工具配置已保存")
            edit_win.destroy()
            self._refresh_tools()

        def reset_defaults():
            if messagebox.askyesno("确认", "确定要恢复默认配置吗？"):
                ToolsService.reset_tool_config(tool_id)
                edit_win.destroy()
                self._refresh_tools()
                messagebox.showinfo("成功", "已恢复默认配置")

        ttk.Button(btn_frame, text="保存", command=save_changes).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="恢复默认", command=reset_defaults).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="取消", command=edit_win.destroy).pack(side=tk.LEFT, padx=5)

    def _refresh_tools(self) -> None:
        """刷新工具列表"""
        for item in self.tools_tree.get_children():
            self.tools_tree.delete(item)

        tools = ToolsService.get_all_tools()
        for tool_id, tool in tools.items():
            status = "已安装" if tool.is_installed() else "未安装"
            self.tools_tree.insert("", tk.END, iid=tool_id, values=(
                tool.name, status, tool.description
            ))

    def _download_selected_tool(self) -> None:
        """下载选中的工具"""
        selected = self.tools_tree.selection()
        if not selected:
            messagebox.showwarning("警告", "请先选择一个工具")
            return

        tool_id = selected[0]
        tool = ToolsService.get_tool(tool_id)
        if not tool:
            return

        action = "更新" if tool.is_installed() else "下载"
        if not messagebox.askyesno("确认", f"确定要{action} {tool.name} 吗？"):
            return

        logger.info(f"开始{action}工具: {tool.name}")

        # 创建进度窗口
        progress_win = tk.Toplevel(self.frame)
        progress_win.title(f"{action} {tool.name}")
        progress_win.geometry("350x120")
        progress_win.resizable(False, False)
        progress_win.transient(self.frame.winfo_toplevel())
        progress_win.grab_set()

        ttk.Label(progress_win, text=f"正在{action} {tool.name}...").pack(pady=15)
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
            # 如果是更新，先卸载
            if tool.is_installed():
                ToolsService.uninstall(tool_id)

            success, msg = ToolsService.download(tool_id, update_progress)
            progress_win.destroy()

            if success:
                logger.info(f"工具{action}成功: {tool.name}")
                messagebox.showinfo("成功", f"{tool.name} {action}完成")
            else:
                logger.error(f"工具{action}失败: {tool.name}, 原因: {msg}")
                messagebox.showerror("错误", msg)

            self._refresh_tools()

        threading.Thread(target=download_thread, daemon=True).start()

    def _uninstall_selected_tool(self) -> None:
        """卸载选中的工具"""
        selected = self.tools_tree.selection()
        if not selected:
            messagebox.showwarning("警告", "请先选择一个工具")
            return

        tool_id = selected[0]
        tool = ToolsService.get_tool(tool_id)
        if not tool:
            return

        if not tool.is_installed():
            messagebox.showinfo("提示", f"{tool.name} 尚未安装")
            return

        if not messagebox.askyesno("确认", f"确定要卸载 {tool.name} 吗？"):
            return

        logger.info(f"开始卸载工具: {tool.name}")
        success, msg = ToolsService.uninstall(tool_id)
        if success:
            logger.info(f"工具卸载成功: {tool.name}")
            messagebox.showinfo("成功", msg)
        else:
            logger.error(f"工具卸载失败: {tool.name}, 原因: {msg}")
            messagebox.showerror("错误", msg)

        self._refresh_tools()

    def _create_buttons(self) -> None:
        """创建按钮"""
        btn_frame = ttk.Frame(self.container)
        btn_frame.pack(fill=tk.X, padx=10, pady=20)

        ttk.Button(
            btn_frame,
            text="保存设置",
            command=self._save_settings
        ).pack(side=tk.LEFT, padx=5)

        ttk.Button(
            btn_frame,
            text="恢复默认",
            command=self._reset_settings
        ).pack(side=tk.LEFT, padx=5)

    def _save_settings(self) -> None:
        """保存设置"""
        try:
            # 验证窗口尺寸
            try:
                width = int(self.window_width_var.get())
                height = int(self.window_height_var.get())
                if width < 400 or height < 300:
                    messagebox.showwarning("警告", "窗口尺寸不能小于 400x300")
                    return
            except ValueError:
                messagebox.showwarning("警告", "请输入有效的窗口尺寸数值")
                return

            # 处理工具目录
            tools_dir = self.tools_dir_var.get().strip()
            default_tools_dir = AppSettings.get_default_tools_dir()
            # 如果是默认目录，保存为空字符串
            if tools_dir == default_tools_dir:
                tools_dir = ""

            # 处理日志目录
            logs_dir = self.logs_dir_var.get().strip()
            default_logs_dir = AppSettings.get_default_logs_dir()
            if logs_dir == default_logs_dir:
                logs_dir = ""

            self.settings.font_size = self.font_size_var.get()
            self.settings.console_log = self.console_log_var.get()
            self.settings.window_width = width
            self.settings.window_height = height
            self.settings.tools_dir = tools_dir
            self.settings.logs_dir = logs_dir
            SettingsService.save(self.settings)
            logger.info(f"设置已保存: font_size={self.settings.font_size}, window={width}x{height}")
            messagebox.showinfo("成功", "设置已保存，部分设置重启后生效")
        except Exception as e:
            logger.error(f"保存设置失败: {e}")
            messagebox.showerror("错误", f"保存设置失败: {e}")

    def _reset_settings(self) -> None:
        """恢复默认设置"""
        self.font_size_var.set(10)
        self.console_log_var.set(False)
        self.window_width_var.set("900")
        self.window_height_var.set("650")
        self.tools_dir_var.set(AppSettings.get_default_tools_dir())
        self.logs_dir_var.set(AppSettings.get_default_logs_dir())
        disable_console_log()
        self.settings = AppSettings()
        SettingsService.save(self.settings)
        logger.info("设置已恢复默认")
        messagebox.showinfo("成功", "已恢复默认设置，重启后生效")
