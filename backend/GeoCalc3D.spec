# -*- mode: python ; coding: utf-8 -*-
"""
3D几何计算器 PyInstaller 打包配置

支持平台:
  - Windows: 打包出 GeoCalc3D.exe(原生 GUI)
  - WSL2(Linux): 打包出 GeoCalc3D 可执行文件(WSLg 显示)

用法(在 backend/ 目录执行):
  cd backend
  .venv/bin/pyinstaller GeoCalc3D.spec

产物:
  dist/GeoCalc3D/           ← 目录版(推荐,QtWebEngine 需要完整目录)
  dist/GeoCalc3D.exe        ← Windows 单文件(可选,用 --onefile)

注意:
  - 前端必须先构建: cd frontend && npm run build
    (产物在 backend/src/ui/,spec 会把它打进包)
  - 示例题目 example_pkl/ 会随包分发
  - log 目录在运行目录自动创建(logger.py 用相对路径)
"""

import sys
from pathlib import Path

# 项目根(本 spec 在 backend/ 下)
# 注意: PyInstaller 的 SPECPATH 就是 spec 所在目录(backend/),不是文件路径!
SPEC_DIR = Path(SPECPATH)                                   # backend/
SRC = SPEC_DIR / 'src'                                      # backend/src/

# 平台判断: Windows 打包 exe,Linux(WSL2)打包 ELF
is_windows = sys.platform.startswith('win')

a = Analysis(
    [str(SRC / 'main.py')],
    pathex=[str(SRC)],                # 让 api/problem/data 可导入
    binaries=[],
    datas=[
        # 前端构建产物(相对路径引用 assets/)
        (str(SRC / 'ui'), 'ui'),
        # 示例题目不打包进程序(用户运行时自己"从文件加载"),
        # 由发布流程单独放进 tar.gz/zip,见 PACKAGING.md
    ],
    hiddenimports=[
        # pywebview 平台后端(自动探测,显式列出保险)
        'webview.platforms.qt',
        # Windows WebView2 链路(winforms 内部导入 edgechromium)
        'webview.platforms.winforms',
        'webview.platforms.edgechromium',
        # 数据层模块(import 链已在 main→api→problem 覆盖,补显式)
        'data.dsl',
        'data_op',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        # 排除无关 GUI 后端
        # Windows: 保留 winforms + edgechromium(WebView2 经 winforms 导入),
        #          排除 PyQt(零 Qt 依赖)
        # Linux(WSL2): 保留 qt,排除 gtk/cocoa/winforms/edgechromium
        'webview.platforms.gtk',
        'webview.platforms.cocoa',
        *(['PyQt5', 'PyQtWebEngine'] if is_windows
          else ['webview.platforms.winforms', 'webview.platforms.edgechromium']),
    ],
    noarchive=False,
    optimize=0,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='GeoCalc3D',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,                     # GUI 程序不弹控制台
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='GeoCalc3D',
)
