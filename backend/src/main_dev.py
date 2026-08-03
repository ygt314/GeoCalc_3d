"""3D几何计算器 - 开发模式入口

与 2D 原版唯一的区别：url 指向你的 Quasar 前端 dev server (localhost:9000)。
开发时你同时要跑两个进程：
  1. frontend/ 里 `npm run dev`（或 pnpm dev）→ 起 9000 端口的 Vite dev server
  2. 本文件 → 起桌面窗口，加载 9000 的页面

debug=True 会开启 CDP 远程调试端口（8228），方便排查前端问题 ——
还记得我们用这个端口抓到的 Object.hasOwn 报错吗？😏
"""

import webview

from api import api

window = webview.create_window(
    '3D几何计算器',           # 窗口标题
    'http://localhost:9000',  # 前端 dev server 地址
    js_api=api,               # 桥接 API
    maximized=True            # 启动即最大化
)
webview.start(debug=True)
