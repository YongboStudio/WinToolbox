# WinToolbox

Windows 系统工具箱 - 基于 Python + Tkinter 的 GUI 工具集

## 功能特性

### 🚀 快捷入口
- 系统设置：环境变量、网络连接、控制面板
- 网络工具：网络适配器、防火墙、资源监视器
- 系统工具：设备管理器、服务管理、任务管理器
- 第三方工具：软件卸载、进程监控、网络连接监控、二维码识别

### 📝 HOSTS 管理
- 查看和编辑 Windows HOSTS 文件
- 快速添加 IP-域名 映射
- 打开 HOSTS 文件所在目录

### 🛣️ 路由管理
- 查看当前路由表
- 添加/删除路由（支持永久路由）

### 🌐 IP 地址
- 查看所有网络适配器信息
- 显示 IPv4、子网掩码、网关、DNS、MAC
- 复制 IP 地址到剪贴板

### 📱 二维码识别
- 识别图片中的二维码内容
- 支持多种图片格式（PNG、JPG、JPEG、BMP、GIF）
- 从文件选择或剪贴板粘贴图片
- 多二维码同时识别
- 增强的剪贴板处理（自动修复截断图片）
- 结果复制到剪贴板
- 备用的"保存剪贴板为文件"功能

### 🔧 Sysinternals Suite
- 集成微软 Sysinternals 工具套件
- 50+ 系统工具一键启动
- 支持搜索过滤

### ⚙️ 设置
- 字体大小调整
- 窗口尺寸设置
- 日志输出控制
- 日志目录自定义
- 第三方工具安装目录设置
- 第三方工具管理（下载/更新/卸载/编辑）

## 项目结构

```
WinToolbox/
├── app.py               # 应用入口
├── pyproject.toml       # 项目配置
├── favicon.ico          # 应用图标
├── run_admin.bat        # 管理员启动脚本
├── services/            # 服务层
│   ├── hosts.py         # HOSTS 服务
│   ├── route.py         # 路由服务
│   ├── network.py       # 网络信息服务
│   ├── settings.py      # 设置服务
│   └── tools.py         # 第三方工具服务
├── ui/                  # UI 层
│   ├── main_window.py   # 主窗口
│   └── tabs/            # 选项卡
│       ├── shortcut.py  # 快捷入口
│       ├── hosts.py     # HOSTS 管理
│       ├── route.py     # 路由管理
│       ├── ip.py        # IP 地址
│       ├── qrcode.py    # 二维码识别
│       ├── sysinternals.py  # Sysinternals
│       ├── settings.py  # 设置
│       └── about.py     # 关于
├── utils/               # 工具模块
│   ├── admin.py         # 管理员权限
│   ├── system.py        # 系统命令
│   └── logger.py        # 日志模块
├── tools/               # 第三方工具目录
└── logs/                # 日志目录
```

## 安装与运行

### 安装 uv（Python 包管理器）

uv 是一个快速的 Python 包管理器，推荐使用。

**Windows (PowerShell):**
```powershell
irm https://astral.sh/uv/install.ps1 | iex
```

**Windows (pip):**
```bash
pip install uv
```

**macOS/Linux:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

更多安装方式请参考：https://docs.astral.sh/uv/getting-started/installation/

### 克隆项目

```bash
git clone https://github.com/YongboStudio/WinToolbox.git
cd WinToolbox
```

### 安装依赖

```bash
uv sync
```

### 运行

**方式一：使用 uv 运行**
```bash
uv run app.py
```

**方式二：直接运行**
```bash
python app.py
```

**方式三：管理员权限运行**

双击 `run_admin.bat`，自动请求管理员权限。

## 开发

### 安装开发依赖

```bash
uv sync --extra dev
```

### 代码检查

```bash
uv run ruff check .
```

### 类型检查

```bash
uv run mypy .
```

### 打包为 exe

```bash
uv run pyinstaller WinToolbox.spec --distpath dist --clean -y
```

## 注意事项

- 修改 HOSTS 文件和路由表需要管理员权限
- 建议以管理员身份运行以获得完整功能
- 日志文件默认保存在 `~/.wintoolbox/logs/` 目录，可在设置中自定义
- 第三方工具默认安装在 `~/.wintoolbox/tools/` 目录，可在设置中自定义
- 设置文件保存在 `~/.wintoolbox/` 目录

## 版本更新

### v1.0.1 (2026-01-12)

**新增功能：**
- 📱 **二维码识别工具**：支持识别图片中的二维码内容
  - 支持多种图片格式（PNG、JPG、JPEG、BMP、GIF）
  - 从文件选择或剪贴板粘贴图片
  - 多二维码同时识别
  - 增强的剪贴板处理（自动修复截断图片）
  - 结果复制到剪贴板
  - 备用的"保存剪贴板为文件"功能
- ⚙️ **设置增强**：
  - 日志目录自定义设置
  - 第三方工具安装目录自定义设置
  - 鼠标滚轮支持（设置页面）

**改进优化：**
- 关于页面版本号从 `pyproject.toml` 动态读取
- 关于页面功能特性从 `README.md` 动态读取
- 构建时间自动生成并显示
- 打包文件名自动包含版本号
- 增强的错误处理和用户提示

**技术更新：**
- 新增依赖：opencv-python、pyzbar、pillow
- 改进 PyInstaller 打包配置
- 优化模块导入和错误处理

### v1.0.0 (2025-12-29)

**初始版本功能：**
- 快捷入口管理
- HOSTS 文件管理
- 路由表管理
- IP 地址查看
- Sysinternals 工具集成
- 系统设置
- 第三方工具管理

## 第三方工具

| 工具 | 描述 | 官网 |
|------|------|------|
| Geek Uninstaller | 高效的软件卸载工具 | https://geekuninstaller.com/ |
| Sysinternals Suite | 微软系统工具套件 | https://learn.microsoft.com/zh-cn/sysinternals/ |

## 许可证

MIT License

## 作者

[YongboStudio](https://github.com/YongboStudio)

## 项目主页

https://github.com/YongboStudio/WinToolbox
