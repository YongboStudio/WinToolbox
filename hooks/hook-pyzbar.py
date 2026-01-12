"""PyInstaller hook for pyzbar"""

from PyInstaller.utils.hooks import collect_data_files, collect_dynamic_libs

# 收集 pyzbar 的数据文件和动态库
datas = collect_data_files('pyzbar')
binaries = collect_dynamic_libs('pyzbar')

# 添加隐藏导入
hiddenimports = ['pyzbar.pyzbar', 'pyzbar.wrapper']