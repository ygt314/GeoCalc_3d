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
- 需先装 Python + uv,重复上面的准备步骤
- **Python 版本**:任意较新版本均可(实测 Python 3.14 打包成功并正常运行)
  —— Windows 版用系统自带 WebView2,**零 Qt 依赖**,不受 PyQt5 版本限制
- 产物 `dist/GeoCalc3D/GeoCalc3D.exe`,整个目录拷走即用
- (可选)用 Inno Setup 制作安装程序 `geocalc3d.exe`

### WSL2(Linux)

- 在 WSL2 里打包出 Linux ELF 可执行文件
- **Python 版本**:3.12(实测正常;3.14 未尝试)
  —— Linux 版依赖 PyQt5,而 PyQt5 5.15.11 没有 3.13+ 的 wheel,只能 3.12
- 运行需要 WSLg:先 `export DISPLAY=:0 WAYLAND_DISPLAY=wayland-0 QT_QPA_PLATFORM=xcb`
- 运行 `./dist/GeoCalc3D/GeoCalc3D`

> **版本差异原因**:两平台 GUI 后端不同 —— Windows 用 WebView2(系统自带,任何 Python 都行),
> Linux 用 PyQt5(锁 3.12)。这是 pyproject 里平台条件依赖(`sys_platform != 'win32'`)的体现。

## 打包内容

| 内容 | 位置 |
|---|---|
| 程序主体 | main.py → GeoCalc3D 可执行文件 |
| 前端界面 | ui/(index.html + assets/) 打进包 |
| 日志 | 运行目录自动创建 log/ |

> 示例题目(example_pkl/)**不打包进程序** —— 用户在运行时通过"从文件加载"自行选择,需要时从仓库获取即可。

## 常见问题

- **前端空白/资源 404**:确认先 `npm run build`,spec 收集的是 `src/ui/` 最新产物
- **log 报错**:log 目录在运行目录自动创建,确保运行目录可写
- **WSL2 无法显示**:确认 DISPLAY/WAYLAND 环境变量 + WSLg 正常
- **防病毒误报**:PyInstaller 打包常见,添加信任即可
