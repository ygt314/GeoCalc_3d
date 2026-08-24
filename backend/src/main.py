"""3D几何计算器 - 正式版入口

加载打包后的前端(build 产物 ui/index.html),无需 dev server。
使用前先构建前端: cd frontend && npm run build
(构建输出到 backend/src/ui,由 quasar.config.ts 的 distDir 指定)
"""

import os
import sys

import webview

from api import api
from logger import backend_logger

__version__ = '1.3.0'

backend_logger.info(f'3D几何计算器，启动！版本：{__version__}')

# 前端资源定位: 打包后 ui/ 在 _internal/ 解包目录,开发时在 src/ 旁
if getattr(sys, 'frozen', False):
    # PyInstaller 打包: ui/ 被打进 _internal(或 exe 同目录)
    base = getattr(sys, '_MEIPASS', os.path.dirname(sys.executable))
    ui_path = os.path.join(base, 'ui', 'index.html')
else:
    ui_path = os.path.join(os.path.dirname(__file__), 'ui', 'index.html')

window = webview.create_window('3D几何计算器', ui_path, js_api=api, maximized=True)
# GUI 后端由 pywebview 自动适配:
# - Windows: 自动用 WebView2(经 winforms 内部导入 edgechromium),零 Qt 依赖
# - Linux/WSL2: 自动探测 GTK → 失败后 fallback 到 Qt(PyQt5)
# 不显式指定,避免触发 winforms 分支(需 pythonnet)或 GTK 探测问题
webview.start()
