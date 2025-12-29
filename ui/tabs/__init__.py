"""选项卡模块"""

from .about import AboutTab
from .hosts import HostsTab
from .ip import IPTab
from .route import RouteTab
from .settings import SettingsTab
from .shortcut import ShortcutTab
from .sysinternals import SysinternalsTab

__all__ = ["ShortcutTab", "HostsTab", "RouteTab", "IPTab", "SysinternalsTab", "SettingsTab", "AboutTab"]
