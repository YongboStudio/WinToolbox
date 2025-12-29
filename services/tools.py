"""第三方工具管理服务"""

import os
import json
import subprocess
import zipfile
import urllib.request
from dataclasses import dataclass, asdict
from typing import Optional, Callable
from utils.logger import logger


@dataclass
class ToolInfo:
    """工具信息"""
    name: str
    description: str
    download_url: str
    exe_name: str
    folder_name: str
    homepage: str = ""
    
    @property
    def install_dir(self) -> str:
        """安装目录"""
        return os.path.join(os.path.dirname(os.path.dirname(__file__)), "tools", self.folder_name)
    
    @property
    def exe_path(self) -> str:
        """可执行文件路径"""
        return os.path.join(self.install_dir, self.exe_name)
    
    def is_installed(self) -> bool:
        """检查是否已安装"""
        return os.path.exists(self.exe_path)


# 默认第三方工具注册表
DEFAULT_TOOLS = {
    "geek_uninstaller": ToolInfo(
        name="Geek Uninstaller",
        description="高效的软件卸载工具",
        download_url="https://geekuninstaller.com/geek.zip",
        exe_name="geek.exe",
        folder_name="geek_uninstaller",
        homepage="https://geekuninstaller.com/"
    ),
    "sysinternals": ToolInfo(
        name="Sysinternals Suite",
        description="微软系统工具套件 (进程监控、磁盘分析等)",
        download_url="https://download.sysinternals.com/files/SysinternalsSuite.zip",
        exe_name="procmon.exe",
        folder_name="sysinternals",
        homepage="https://learn.microsoft.com/zh-cn/sysinternals/"
    ),
}


class ToolsService:
    """第三方工具管理服务"""
    
    _tools: Optional[dict[str, ToolInfo]] = None
    _config_dir = os.path.join(os.path.expanduser("~"), ".wintoolbox")
    _config_file = os.path.join(_config_dir, "tools.json")
    
    @classmethod
    def _load_tools(cls) -> dict[str, ToolInfo]:
        """加载工具配置"""
        tools = {k: ToolInfo(**asdict(v)) for k, v in DEFAULT_TOOLS.items()}
        
        # 加载自定义配置
        try:
            if os.path.exists(cls._config_file):
                with open(cls._config_file, "r", encoding="utf-8") as f:
                    custom = json.load(f)
                # 合并自定义 URL
                for tool_id, config in custom.items():
                    if tool_id in tools:
                        if "download_url" in config:
                            tools[tool_id].download_url = config["download_url"]
                        if "homepage" in config:
                            tools[tool_id].homepage = config["homepage"]
        except Exception as e:
            logger.error(f"加载工具配置失败: {e}")
        
        return tools
    
    @classmethod
    def _save_tools(cls) -> None:
        """保存工具配置"""
        if cls._tools is None:
            return
        
        try:
            os.makedirs(cls._config_dir, exist_ok=True)
            
            # 只保存与默认值不同的配置
            custom = {}
            for tool_id, tool in cls._tools.items():
                if tool_id in DEFAULT_TOOLS:
                    default = DEFAULT_TOOLS[tool_id]
                    diff = {}
                    if tool.download_url != default.download_url:
                        diff["download_url"] = tool.download_url
                    if tool.homepage != default.homepage:
                        diff["homepage"] = tool.homepage
                    if diff:
                        custom[tool_id] = diff
            
            with open(cls._config_file, "w", encoding="utf-8") as f:
                json.dump(custom, f, indent=2, ensure_ascii=False)
            
            logger.info("工具配置已保存")
        except Exception as e:
            logger.error(f"保存工具配置失败: {e}")
    
    @classmethod
    def get_tool(cls, tool_id: str) -> Optional[ToolInfo]:
        """获取工具信息"""
        if cls._tools is None:
            cls._tools = cls._load_tools()
        return cls._tools.get(tool_id)
    
    @classmethod
    def get_all_tools(cls) -> dict[str, ToolInfo]:
        """获取所有工具"""
        if cls._tools is None:
            cls._tools = cls._load_tools()
        return cls._tools.copy()
    
    @classmethod
    def update_tool_url(cls, tool_id: str, download_url: str) -> bool:
        """更新工具下载地址"""
        if cls._tools is None:
            cls._tools = cls._load_tools()
        
        if tool_id not in cls._tools:
            return False
        
        cls._tools[tool_id].download_url = download_url
        cls._save_tools()
        logger.info(f"工具 {tool_id} 下载地址已更新: {download_url}")
        return True
    
    @classmethod
    def update_tool_homepage(cls, tool_id: str, homepage: str) -> bool:
        """更新工具主页"""
        if cls._tools is None:
            cls._tools = cls._load_tools()
        
        if tool_id not in cls._tools:
            return False
        
        cls._tools[tool_id].homepage = homepage
        cls._save_tools()
        logger.info(f"工具 {tool_id} 主页已更新: {homepage}")
        return True
    
    @classmethod
    def reset_tool_config(cls, tool_id: str) -> bool:
        """重置工具配置为默认值"""
        if tool_id not in DEFAULT_TOOLS:
            return False
        
        if cls._tools is None:
            cls._tools = cls._load_tools()
        
        default = DEFAULT_TOOLS[tool_id]
        cls._tools[tool_id].download_url = default.download_url
        cls._tools[tool_id].homepage = default.homepage
        cls._save_tools()
        logger.info(f"工具 {tool_id} 配置已重置")
        return True
    
    @classmethod
    def launch(cls, tool_id: str) -> tuple[bool, str]:
        """启动工具"""
        tool = cls.get_tool(tool_id)
        if not tool:
            logger.warning(f"尝试启动不存在的工具: {tool_id}")
            return False, "工具不存在"
        
        if not tool.is_installed():
            logger.warning(f"尝试启动未安装的工具: {tool.name}")
            return False, "工具未安装"
        
        try:
            logger.info(f"启动工具: {tool.name}, 路径: {tool.exe_path}")
            subprocess.Popen(
                [tool.exe_path],
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            return True, "启动成功"
        except Exception as e:
            logger.error(f"启动工具失败: {tool.name}, 错误: {e}")
            return False, f"启动失败: {e}"
    
    @classmethod
    def download(cls, tool_id: str, progress_callback: Optional[Callable[[int, int], None]] = None) -> tuple[bool, str]:
        """下载并安装工具"""
        tool = cls.get_tool(tool_id)
        if not tool:
            return False, "工具不存在"
        
        logger.info(f"开始下载工具: {tool.name}, URL: {tool.download_url}")
        
        try:
            # 创建目录
            os.makedirs(tool.install_dir, exist_ok=True)
            logger.debug(f"创建安装目录: {tool.install_dir}")
            
            # 下载文件
            zip_path = os.path.join(tool.install_dir, "download.zip")
            
            def report_hook(block_num, block_size, total_size):
                if progress_callback and total_size > 0:
                    downloaded = block_num * block_size
                    progress_callback(downloaded, total_size)
            
            logger.debug(f"下载文件到: {zip_path}")
            urllib.request.urlretrieve(tool.download_url, zip_path, report_hook)
            
            # 解压
            logger.debug(f"解压文件: {zip_path}")
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(tool.install_dir)
            
            # 删除压缩包
            os.remove(zip_path)
            logger.debug("删除临时压缩包")
            
            if tool.is_installed():
                logger.info(f"工具安装成功: {tool.name}")
                return True, "安装成功"
            else:
                logger.error(f"工具安装失败: {tool.name}, 未找到可执行文件")
                return False, "安装失败：未找到可执行文件"
                
        except Exception as e:
            logger.error(f"下载工具失败: {tool.name}, 错误: {e}")
            return False, f"下载失败: {e}"
    
    @classmethod
    def uninstall(cls, tool_id: str) -> tuple[bool, str]:
        """卸载工具"""
        tool = cls.get_tool(tool_id)
        if not tool:
            return False, "工具不存在"
        
        if not tool.is_installed():
            return False, "工具未安装"
        
        logger.info(f"开始卸载工具: {tool.name}")
        
        try:
            import shutil
            shutil.rmtree(tool.install_dir)
            logger.info(f"工具卸载成功: {tool.name}")
            return True, "卸载成功"
        except Exception as e:
            logger.error(f"卸载工具失败: {tool.name}, 错误: {e}")
            return False, f"卸载失败: {e}"
