# Windows 系统工具箱

基于 Python + tkinter 的 Windows 系统管理 GUI 工具。

## 功能

1. **快捷入口** - 常用系统设置快捷方式（环境变量、网络连接、防火墙等）
2. **HOSTS 管理** - 查看/编辑 hosts 文件，快速添加条目
3. **路由管理** - 查看路由表，增删路由（支持永久路由）
4. **IP 地址** - 查看网络适配器信息（IP、掩码、网关、DNS、MAC）

## 项目结构

```
WinToolbox/
├── __init__.py          # 包初始化
├── app.py               # 应用入口
├── utils/               # 工具模块
│   ├── admin.py         # 管理员权限
│   └── system.py        # 系统命令
├── services/            # 服务层
│   ├── hosts.py         # HOSTS 服务
│   ├── route.py         # 路由服务
│   └── network.py       # 网络信息服务
└── ui/                  # UI 层
    ├── main_window.py   # 主窗口
    └── tabs/            # 选项卡
        ├── base.py      # 基类
        ├── shortcut.py  # 快捷入口
        ├── hosts.py     # HOSTS 管理
        ├── route.py     # 路由管理
        ├── ip.py        # IP 地址
        └── about.py     # 关于
```

## 运行方式

### 方式一：直接运行
```bash
python main.py
```

### 方式二：作为模块运行
```bash
python -m WinToolbox.app
```

### 方式三：管理员启动脚本
双击 `run_admin.bat`，自动请求管理员权限。

## 开发

安装开发依赖：
```bash
pip install -e ".[dev]"
```

打包为 exe：
```bash
pyinstaller --onefile --windowed --icon=favicon.ico main.py
```

## 注意事项

- 修改 HOSTS 文件和路由表需要管理员权限
- 建议以管理员身份运行以获得完整功能
