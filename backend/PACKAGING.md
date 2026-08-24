# 打包指南(GeoCalc3D)

项目功能完整后,用 PyInstaller 打包成独立可执行程序。

## 准备工作(两平台通用)

```bash
# 1. 构建前端(产物到 backend/src/ui)
cd frontend && npm install && npm run build

# 2. 安装打包工具(backend venv)
cd backend
uv pip install pyinstaller
```

## 打包

```bash
cd backend
.venv/bin/pyinstaller GeoCalc3D.spec --noconfirm
```

产物:`backend/dist/GeoCalc3D/`(目录版)

## 平台说明

### Windows(原生 exe)

- 在 **Windows 上** 执行打包(不能跨平台交叉编译)
- 需先装 Python 3.12 + uv,重复上面的准备步骤
- 产物 `dist/GeoCalc3D/GeoCalc3D.exe`,整个目录拷走即用
- QtWebEngine 需要完整目录(PyQt5 的 QtWebEngineProcess 等),**不要用 --onefile 单文件**

### WSL2(Linux)

- 在 WSL2 里打包出 Linux ELF 可执行文件
- 运行需要 WSLg:先 `export DISPLAY=:0 WAYLAND_DISPLAY=wayland-0 QT_QPA_PLATFORM=xcb`
- 运行 `./dist/GeoCalc3D/GeoCalc3D`

## 打包内容

| 内容 | 位置 |
|---|---|
| 程序主体 | main.py → GeoCalc3D 可执行文件 |
| 前端界面 | ui/(index.html + assets/) 打进包 |
| 示例题目 | example_pkl/(GC1/GC2 高考真题 + 文档) |
| 日志 | 运行目录自动创建 log/ |

## 常见问题

- **前端空白/资源 404**:确认先 `npm run build`,spec 收集的是 `src/ui/` 最新产物
- **log 报错**:log 目录在运行目录自动创建,确保运行目录可写
- **WSL2 无法显示**:确认 DISPLAY/WAYLAND 环境变量 + WSLg 正常
- **防病毒误报**:PyInstaller 打包常见,添加信任即可
