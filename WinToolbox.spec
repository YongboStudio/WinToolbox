# -*- mode: python ; coding: utf-8 -*-

import os
import tomllib
from datetime import datetime
from PyInstaller.utils.hooks import collect_submodules

block_cipher = None
workdir = os.path.abspath('.')

# 从 pyproject.toml 读取版本号
with open('pyproject.toml', 'rb') as f:
    pyproject = tomllib.load(f)
    VERSION = pyproject['project']['version']

# 生成构建时间文件
BUILD_TIME = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
with open('buildtime.txt', 'w', encoding='utf-8') as f:
    f.write(BUILD_TIME)

# 收集所有本地模块
hiddenimports = []
hiddenimports += collect_submodules('services')
hiddenimports += collect_submodules('ui')
hiddenimports += collect_submodules('utils')

a = Analysis(
    ['app.py'],
    pathex=[workdir],
    binaries=[],
    datas=[
        ('favicon.ico', '.'),
        ('buildtime.txt', '.'),
        ('README.md', '.'),
        ('pyproject.toml', '.'),
        ('services', 'services'),
        ('ui', 'ui'),
        ('utils', 'utils'),
    ],
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name=f'WinToolbox-{VERSION}',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['favicon.ico'],
)
