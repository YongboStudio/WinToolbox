"""选项卡模块"""

from .about import AboutTab
from .hosts import HostsTab
from .ip import IPTab
from .qrcode import QRCodeTab
from .route import RouteTab
from .settings import SettingsTab
from .shortcut import ShortcutTab
from .sysinternals import SysinternalsTab

__all__ = ["ShortcutTab", "HostsTab", "RouteTab", "IPTab", "QRCodeTab", "SysinternalsTab", "SettingsTab", "AboutTab"]
