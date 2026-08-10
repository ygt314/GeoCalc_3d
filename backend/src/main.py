"""3D几何计算器 - 正式版入口

加载打包后的前端(build 产物 ui/index.html),无需 dev server。
使用前先构建前端: cd frontend && npm run build
(构建输出到 backend/src/ui,由 quasar.config.ts 的 distDir 指定)
"""

import webview

from api import api
from logger import backend_logger

__version__ = '0.1.0'

backend_logger.info(f'3D几何计算器，启动！版本：{__version__}')

window = webview.create_window('3D几何计算器', 'ui/index.html', js_api=api, maximized=True)
webview.start()
