"""3D几何计算器 - 构建后处理脚本

Quasar 构建产物的资源路径是绝对路径(/assets/...),
而正式版由 pywebview 通过 file:// 加载本地 HTML,绝对路径会指向文件系统根。
本脚本把 index.html 里的 /assets/... 改写为相对路径 assets/...。

用法: cd frontend && npm run build && python3 fix_ui_paths.py
"""

import re
from pathlib import Path

UI_DIR = Path(__file__).parent / 'src' / 'ui'
INDEX = UI_DIR / 'index.html'


def main():
    html = INDEX.read_text(encoding='utf-8')
    # /assets/xxx → assets/xxx(去掉开头的 /)
    fixed = html.replace('src="/assets/', 'src="assets/').replace('href="/assets/', 'href="assets/')
    count = fixed.count('src="assets/') + fixed.count('href="assets/')
    INDEX.write_text(fixed, encoding='utf-8')
    print(f'已修正资源路径为相对路径,共 {count} 处')


if __name__ == '__main__':
    main()
