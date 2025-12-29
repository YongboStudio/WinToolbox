"""路由管理服务"""

from dataclasses import dataclass
from typing import Optional
from utils.system import run_command
from utils.logger import logger


@dataclass
class RouteEntry:
    """路由条目"""
    destination: str
    mask: str
    gateway: str
    interface: str
    metric: str


class RouteService:
    """路由管理服务"""
    
    @classmethod
    def get_routes(cls) -> list[RouteEntry]:
        """获取路由表"""
        logger.debug("获取路由表")
        result = run_command(["route", "print", "-4"])
        routes = cls._parse_routes(result.stdout)
        logger.debug(f"解析到 {len(routes)} 条路由")
        return routes
    
    @classmethod
    def _parse_routes(cls, output: str) -> list[RouteEntry]:
        """解析路由表输出"""
        routes = []
        lines = output.split("\n")
        in_route_table = False
        
        for line in lines:
            line = line.strip()
            if "Network Destination" in line or "网络目标" in line:
                in_route_table = True
                continue
            if in_route_table and line:
                if "==" in line or not line[0].isdigit():
                    in_route_table = False
                    continue
                parts = line.split()
                if len(parts) >= 5:
                    routes.append(RouteEntry(
                        destination=parts[0],
                        mask=parts[1],
                        gateway=parts[2],
                        interface=parts[3],
                        metric=parts[4]
                    ))
        return routes
    
    @classmethod
    def add(
        cls,
        destination: str,
        mask: str,
        gateway: str,
        metric: Optional[str] = None,
        persistent: bool = False
    ) -> tuple[bool, str]:
        """添加路由"""
        cmd = ["route"]
        if persistent:
            cmd.append("-p")
        cmd.extend(["add", destination, "mask", mask, gateway])
        if metric:
            cmd.extend(["metric", metric])
        
        logger.info(f"添加路由: {destination} mask {mask} gateway {gateway}, persistent={persistent}")
        result = run_command(cmd)
        success = result.returncode == 0
        message = "路由添加成功" if success else (result.stderr or result.stdout)
        
        if success:
            logger.info(f"路由添加成功: {destination}")
        else:
            logger.error(f"路由添加失败: {destination}, 原因: {message}")
        
        return success, message
    
    @classmethod
    def delete(cls, destination: str) -> tuple[bool, str]:
        """删除路由"""
        logger.info(f"删除路由: {destination}")
        result = run_command(["route", "delete", destination])
        success = result.returncode == 0
        message = "路由删除成功" if success else (result.stderr or result.stdout)
        
        if success:
            logger.info(f"路由删除成功: {destination}")
        else:
            logger.error(f"路由删除失败: {destination}, 原因: {message}")
        
        return success, message
