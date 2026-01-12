"""二维码识别选项卡"""

import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from typing import Optional

from utils.logger import logger

from .base import BaseTab

try:
    import cv2
    import numpy as np
    from PIL import Image, ImageFile, ImageTk
    from pyzbar import pyzbar
    
    # 启用截断图片加载
    ImageFile.LOAD_TRUNCATED_IMAGES = True
    
    DEPS_AVAILABLE = True
    DEPS_ERROR = None
except ImportError as e:
    DEPS_AVAILABLE = False
    DEPS_ERROR = f"缺少依赖库: {e}"
except Exception as e:
    DEPS_AVAILABLE = False
    DEPS_ERROR = f"依赖库加载失败: {e}"


class QRCodeTab(BaseTab):
    """二维码识别选项卡"""

    def setup_ui(self) -> None:
        """设置 UI 界面"""
        if not DEPS_AVAILABLE:
            self._show_dependency_error()
            return

        # 标题
        title_label = ttk.Label(
            self.frame,
            text="二维码识别工具",
            font=("Microsoft YaHei UI", 16, "bold")
        )
        title_label.pack(pady=20)

        # 主容器
        main_frame = ttk.Frame(self.frame)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        # 左侧：图片显示区域
        left_frame = ttk.LabelFrame(main_frame, text="图片预览")
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))

        # 图片显示画布
        self.canvas = tk.Canvas(left_frame, bg="white", width=400, height=300)
        self.canvas.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # 右侧：控制和结果区域
        right_frame = ttk.Frame(main_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=(10, 0))

        # 文件选择区域
        file_frame = ttk.LabelFrame(right_frame, text="文件操作")
        file_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Button(
            file_frame,
            text="选择图片文件",
            command=self._select_image_file
        ).pack(fill=tk.X, padx=10, pady=5)

        ttk.Button(
            file_frame,
            text="从剪贴板粘贴",
            command=self._paste_from_clipboard
        ).pack(fill=tk.X, padx=10, pady=5)

        ttk.Button(
            file_frame,
            text="保存剪贴板为文件",
            command=self._save_clipboard_to_file
        ).pack(fill=tk.X, padx=10, pady=5)

        ttk.Button(
            file_frame,
            text="清空",
            command=self._clear_image
        ).pack(fill=tk.X, padx=10, pady=5)

        # 识别结果区域
        result_frame = ttk.LabelFrame(right_frame, text="识别结果")
        result_frame.pack(fill=tk.BOTH, expand=True, pady=(10, 0))

        # 结果文本框
        self.result_text = tk.Text(
            result_frame,
            wrap=tk.WORD,
            font=("Microsoft YaHei UI", 10),
            width=40,
            height=15
        )
        result_scrollbar = ttk.Scrollbar(result_frame, orient="vertical", command=self.result_text.yview)
        self.result_text.configure(yscrollcommand=result_scrollbar.set)

        self.result_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(10, 0), pady=10)
        result_scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=10)

        # 结果操作按钮
        result_btn_frame = ttk.Frame(result_frame)
        result_btn_frame.pack(fill=tk.X, padx=10, pady=(0, 10))

        ttk.Button(
            result_btn_frame,
            text="复制结果",
            command=self._copy_result
        ).pack(fill=tk.X, pady=(0, 5))

        ttk.Button(
            result_btn_frame,
            text="仅复制内容",
            command=self._copy_content_only
        ).pack(fill=tk.X, pady=5)

        ttk.Button(
            result_btn_frame,
            text="清空结果",
            command=self._clear_result
        ).pack(fill=tk.X, pady=(5, 0))

        # 初始化变量
        self.current_image: Optional[Image.Image] = None
        self.photo_image: Optional[ImageTk.PhotoImage] = None
        self.qr_contents: list[str] = []  # 存储识别出的二维码内容

        # 显示使用说明
        self._show_usage_info()

    def _show_dependency_error(self) -> None:
        """显示依赖缺失错误"""
        error_label = ttk.Label(
            self.frame,
            text="二维码识别功能不可用",
            font=("Microsoft YaHei UI", 16, "bold"),
            foreground="red"
        )
        error_label.pack(pady=50)

        # 显示具体错误信息
        if DEPS_ERROR:
            error_detail = ttk.Label(
                self.frame,
                text=f"错误详情：{DEPS_ERROR}",
                font=("Microsoft YaHei UI", 10),
                foreground="red"
            )
            error_detail.pack(pady=10)

        info_text = """
        二维码识别功能需要以下依赖库：
        • opencv-python (图像处理)
        • pyzbar (二维码识别)
        • pillow (图像处理)

        解决方案：
        1. 开发模式：运行 uv sync 安装依赖
        2. 打包版本：可能需要手动安装 zbar 库
        
        备用方案：
        • 使用在线二维码识别工具
        • 使用手机扫码应用
        """

        info_label = ttk.Label(
            self.frame,
            text=info_text,
            font=("Microsoft YaHei UI", 10),
            justify=tk.LEFT
        )
        info_label.pack(pady=20)

    def _show_usage_info(self) -> None:
        """显示使用说明"""
        usage_info = """使用说明：
1. 点击"选择图片文件"选择包含二维码的图片
2. 或点击"从剪贴板粘贴"粘贴剪贴板中的图片
3. 程序会自动识别图片中的二维码内容
4. 识别结果显示在右侧文本框中
5. 可以复制识别结果到剪贴板

支持的图片格式：
• PNG、JPG、JPEG、BMP、GIF
• 支持多个二维码同时识别"""

        self.result_text.insert(tk.END, usage_info)
        self.result_text.config(state=tk.DISABLED)

    def _select_image_file(self) -> None:
        """选择图片文件"""
        file_types = [
            ("图片文件", "*.png *.jpg *.jpeg *.bmp *.gif"),
            ("PNG文件", "*.png"),
            ("JPEG文件", "*.jpg *.jpeg"),
            ("所有文件", "*.*")
        ]

        file_path = filedialog.askopenfilename(
            title="选择包含二维码的图片",
            filetypes=file_types
        )

        if file_path:
            self._load_image_from_file(file_path)

    def _paste_from_clipboard(self) -> None:
        """从剪贴板粘贴图片"""
        try:
            # 尝试从剪贴板获取图片
            from PIL import ImageGrab
            
            # 先尝试直接获取图片
            image = ImageGrab.grabclipboard()
            
            if image is None:
                # 如果直接获取失败，尝试从文件路径获取
                try:
                    import win32clipboard
                    win32clipboard.OpenClipboard()
                    
                    # 检查是否有文件路径
                    if win32clipboard.IsClipboardFormatAvailable(win32clipboard.CF_HDROP):
                        files = win32clipboard.GetClipboardData(win32clipboard.CF_HDROP)
                        win32clipboard.CloseClipboard()
                        
                        if files and len(files) > 0:
                            file_path = files[0]
                            # 检查是否是图片文件
                            if file_path.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif')):
                                self._load_image_from_file(file_path)
                                return
                    else:
                        win32clipboard.CloseClipboard()
                except ImportError:
                    pass  # win32clipboard 不可用
                except Exception:
                    try:
                        win32clipboard.CloseClipboard()
                    except:
                        pass
                
                messagebox.showwarning("警告", "剪贴板中没有图片或图片文件")
                return

            if not isinstance(image, Image.Image):
                messagebox.showwarning("警告", "剪贴板内容不是有效的图片")
                return

            # 验证图片数据完整性
            try:
                # 尝试加载图片数据
                image.load()
                
                # 如果图片格式有问题，尝试重新保存为 PNG
                if hasattr(image, 'format') and image.format in ['JPEG', 'JPG']:
                    # JPEG 可能有截断问题，转换为 PNG
                    import io
                    buffer = io.BytesIO()
                    image.save(buffer, format='PNG')
                    buffer.seek(0)
                    image = Image.open(buffer)
                    image.load()
                
            except Exception as e:
                logger.warning(f"图片数据可能不完整，尝试修复: {e}")
                
                # 尝试修复截断的图片
                try:
                    from PIL import ImageFile
                    ImageFile.LOAD_TRUNCATED_IMAGES = True
                    
                    # 重新尝试加载
                    image.load()
                    
                except Exception as e2:
                    logger.error(f"无法修复图片数据: {e2}")
                    messagebox.showerror("错误", f"图片数据损坏或不完整，无法处理\n\n建议：\n1. 重新复制图片\n2. 或保存图片后选择文件加载")
                    return

            self._load_image(image)
            logger.info("从剪贴板加载图片成功")

        except Exception as e:
            logger.error(f"从剪贴板粘贴图片失败: {e}")
            messagebox.showerror("错误", f"从剪贴板粘贴失败: {e}\n\n建议：\n1. 重新复制图片\n2. 或使用\"选择图片文件\"功能")

    def _save_clipboard_to_file(self) -> None:
        """保存剪贴板内容为文件"""
        try:
            from PIL import ImageGrab
            from tkinter import filedialog
            import os
            
            image = ImageGrab.grabclipboard()
            
            if image is None:
                messagebox.showwarning("警告", "剪贴板中没有图片")
                return

            if not isinstance(image, Image.Image):
                messagebox.showwarning("警告", "剪贴板内容不是有效的图片")
                return

            # 选择保存位置
            file_path = filedialog.asksaveasfilename(
                title="保存剪贴板图片",
                defaultextension=".png",
                filetypes=[
                    ("PNG文件", "*.png"),
                    ("JPEG文件", "*.jpg"),
                    ("所有文件", "*.*")
                ]
            )
            
            if not file_path:
                return
            
            # 保存图片
            if file_path.lower().endswith('.jpg') or file_path.lower().endswith('.jpeg'):
                # JPEG 格式需要转换为 RGB
                if image.mode in ('RGBA', 'LA', 'P'):
                    background = Image.new('RGB', image.size, (255, 255, 255))
                    if image.mode == 'P':
                        image = image.convert('RGBA')
                    background.paste(image, mask=image.split()[-1] if image.mode == 'RGBA' else None)
                    image = background
                image.save(file_path, 'JPEG', quality=95)
            else:
                image.save(file_path, 'PNG')
            
            messagebox.showinfo("成功", f"图片已保存到：\n{file_path}\n\n现在可以使用\"选择图片文件\"功能加载此文件")
            logger.info(f"剪贴板图片已保存到: {file_path}")
            
        except Exception as e:
            logger.error(f"保存剪贴板图片失败: {e}")
            messagebox.showerror("错误", f"保存失败: {e}")

    def _load_image_from_file(self, file_path: str) -> None:
        """从文件加载图片"""
        try:
            image = Image.open(file_path)
            self._load_image(image)
            logger.info(f"加载图片文件成功: {file_path}")
        except Exception as e:
            logger.error(f"加载图片文件失败: {file_path}, 错误: {e}")
            messagebox.showerror("错误", f"加载图片失败: {e}")

    def _load_image(self, image: Image.Image) -> None:
        """加载并显示图片"""
        self.current_image = image.copy()
        
        # 显示图片
        self._display_image(image)
        
        # 识别二维码
        self._recognize_qrcodes(image)

    def _display_image(self, image: Image.Image) -> None:
        """在画布上显示图片"""
        # 获取画布尺寸
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        
        if canvas_width <= 1 or canvas_height <= 1:
            # 画布还没有正确初始化，使用默认尺寸
            canvas_width, canvas_height = 400, 300

        # 计算缩放比例
        img_width, img_height = image.size
        scale_x = canvas_width / img_width
        scale_y = canvas_height / img_height
        scale = min(scale_x, scale_y, 1.0)  # 不放大，只缩小

        # 缩放图片
        new_width = int(img_width * scale)
        new_height = int(img_height * scale)
        resized_image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)

        # 转换为 PhotoImage
        self.photo_image = ImageTk.PhotoImage(resized_image)

        # 清空画布并显示图片
        self.canvas.delete("all")
        x = (canvas_width - new_width) // 2
        y = (canvas_height - new_height) // 2
        self.canvas.create_image(x, y, anchor=tk.NW, image=self.photo_image)

    def _recognize_qrcodes(self, image: Image.Image) -> None:
        """识别图片中的二维码"""
        try:
            # 转换为 OpenCV 格式
            cv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
            
            # 识别二维码
            qr_codes = pyzbar.decode(cv_image)
            
            # 清空结果和内容
            self._clear_result()
            self.qr_contents.clear()
            
            if not qr_codes:
                self.result_text.config(state=tk.NORMAL)
                self.result_text.insert(tk.END, "未检测到二维码\n\n")
                self.result_text.insert(tk.END, "提示：\n")
                self.result_text.insert(tk.END, "• 确保图片清晰，二维码完整\n")
                self.result_text.insert(tk.END, "• 尝试调整图片亮度和对比度\n")
                self.result_text.insert(tk.END, "• 确保二维码在图片中占据足够大的区域")
                self.result_text.config(state=tk.DISABLED)
                logger.info("图片中未检测到二维码")
                return

            # 显示识别结果
            self.result_text.config(state=tk.NORMAL)
            self.result_text.insert(tk.END, f"检测到 {len(qr_codes)} 个二维码：\n\n")
            
            for i, qr_code in enumerate(qr_codes, 1):
                # 解码内容
                try:
                    content = qr_code.data.decode('utf-8')
                except UnicodeDecodeError:
                    content = qr_code.data.decode('gbk', errors='ignore')
                
                # 保存内容到列表
                self.qr_contents.append(content)
                
                # 显示结果
                self.result_text.insert(tk.END, f"二维码 {i}：\n")
                self.result_text.insert(tk.END, f"类型：{qr_code.type}\n")
                self.result_text.insert(tk.END, f"内容：{content}\n")
                
                # 显示位置信息
                rect = qr_code.rect
                self.result_text.insert(tk.END, f"位置：({rect.left}, {rect.top}) - ({rect.left + rect.width}, {rect.top + rect.height})\n")
                self.result_text.insert(tk.END, "-" * 50 + "\n\n")

            self.result_text.config(state=tk.DISABLED)
            logger.info(f"成功识别 {len(qr_codes)} 个二维码")

        except Exception as e:
            logger.error(f"二维码识别失败: {e}")
            self._clear_result()
            self.qr_contents.clear()
            self.result_text.config(state=tk.NORMAL)
            self.result_text.insert(tk.END, f"识别失败：{e}")
            self.result_text.config(state=tk.DISABLED)

    def _copy_result(self) -> None:
        """复制识别结果到剪贴板"""
        content = self.result_text.get(1.0, tk.END).strip()
        if content:
            self.frame.clipboard_clear()
            self.frame.clipboard_append(content)
            messagebox.showinfo("成功", "识别结果已复制到剪贴板")
        else:
            messagebox.showwarning("警告", "没有可复制的内容")

    def _copy_content_only(self) -> None:
        """仅复制二维码内容到剪贴板"""
        if not self.qr_contents:
            messagebox.showwarning("警告", "没有可复制的二维码内容")
            return
        
        # 如果只有一个二维码，直接复制内容
        if len(self.qr_contents) == 1:
            content = self.qr_contents[0]
        else:
            # 多个二维码时，每行一个内容
            content = "\n".join(self.qr_contents)
        
        self.frame.clipboard_clear()
        self.frame.clipboard_append(content)
        
        count = len(self.qr_contents)
        if count == 1:
            messagebox.showinfo("成功", "二维码内容已复制到剪贴板")
        else:
            messagebox.showinfo("成功", f"{count} 个二维码内容已复制到剪贴板\n(每行一个内容)")
        
        logger.info(f"复制了 {count} 个二维码的内容")

    def _clear_result(self) -> None:
        """清空识别结果"""
        self.result_text.config(state=tk.NORMAL)
        self.result_text.delete(1.0, tk.END)
        self.result_text.config(state=tk.DISABLED)
        self.qr_contents.clear()  # 清空内容列表

    def _clear_image(self) -> None:
        """清空图片和结果"""
        self.canvas.delete("all")
        self.current_image = None
        self.photo_image = None
        self._clear_result()
        self._show_usage_info()
        logger.info("已清空图片和识别结果")