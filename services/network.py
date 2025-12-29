"""网络信息服务"""

import re
from dataclasses import dataclass, field
from typing import Optional
from utils.system import run_command


@dataclass
class AdapterInfo:
    """网络适配器信息"""
    name: str = ""
    ipv4: str = ""
    mask: str = ""
    gateway: str = ""
    dns: str = ""
    mac: str = ""


class NetworkService:
    """网络信息服务"""
    
    @classmethod
    def get_ipconfig_output(cls) -> str:
        """获取 ipconfig /all 输出"""
        result = run_command(["ipconfig", "/all"])
        return result.stdout
    
    @classmethod
    def get_adapters(cls) -> list[AdapterInfo]:
        """获取所有网络适配器信息"""
        output = cls.get_ipconfig_output()
        return cls._parse_ipconfig(output)
    
    @classmethod
    def _parse_ipconfig(cls, output: str) -> list[AdapterInfo]:
        """解析 ipconfig 输出"""
        adapters = []
        current: Optional[AdapterInfo] = None
        
        for line in output.split("\n"):
            # 检测适配器名称
            if "适配器" in line or "adapter" in line.lower():
                if current and current.ipv4:
                    adapters.append(current)
                name = line.replace(":", "").strip()
                current = AdapterInfo(name=name)
            elif current:
                line = line.strip()
                cls._parse_adapter_line(current, line)
        
        # 添加最后一个适配器
        if current and current.ipv4:
            adapters.append(current)
        
        return adapters
    
    @classmethod
    def _parse_adapter_line(cls, adapter: AdapterInfo, line: str) -> None:
        """解析适配器信息行"""
        ip_pattern = r"(\d+\.\d+\.\d+\.\d+)"
        mac_pattern = r"([0-9A-Fa-f-]{17})"
        
        if "IPv4" in line or "IP Address" in line:
            match = re.search(ip_pattern, line)
            if match:
                adapter.ipv4 = match.group(1)
        elif "子网掩码" in line or "Subnet Mask" in line:
            match = re.search(ip_pattern, line)
            if match:
                adapter.mask = match.group(1)
        elif "默认网关" in line or "Default Gateway" in line:
            match = re.search(ip_pattern, line)
            if match:
                adapter.gateway = match.group(1)
        elif "DNS 服务器" in line or "DNS Servers" in line:
            match = re.search(ip_pattern, line)
            if match:
                adapter.dns = match.group(1)
        elif "物理地址" in line or "Physical Address" in line:
            match = re.search(mac_pattern, line)
            if match:
                adapter.mac = match.group(1)
