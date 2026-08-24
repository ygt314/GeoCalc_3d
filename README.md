# 3D几何计算器 (GeoCalc_3d)

> 一个学习项目：用 SymPy 暴力计算立体几何 —— 3D 版 [GeometryCalculator](https://github.com/zhdbk3/GeometryCalculator)

## 简介

这是一个**学习项目**，原型是[着火的冰块nya](https://b23.tv/IstwV1E)的 [GeometryCalculator](https://github.com/zhdbk3/GeometryCalculator)（GPL-3.0）。

它把高中立体几何（点、线、面、向量、距离、角度、体积、极值）变成**可输入、可求解**的交互工具：
- 添加点（3D 坐标或约束）、添加符号（未知数）、添加条件（平行/垂直/等距）
- 求解任意表达式：`AB`（距离）、`angABC`（角度）、`vABCD`（四面体体积）等
- **极值探索**：对表达式求偏导解驻点（附函数值）
- **函数值探索**：给定变量取值，精确 + 浮点双显示
- 支持嵌套根号化简（`sqrtdenest`，参考[原版 issue #5](https://github.com/zhdbk3/GeometryCalculator/issues/5)）

## 技术栈

| 层 | 技术 |
|---|---|
| 后端 | Python 3.12+（Windows 支持最新版,Linux 需 3.12）+ SymPy + pywebview |
| GUI | PyQt5 / QtWebEngine（Chromium 87） |
| 前端 | Quasar (Vue 3) + KaTeX（公式渲染） |
| 测试 | pytest（115 个单元测试全绿） |

---

# 使用（普通用户）

> 不想碰代码？直接从 [Releases](https://gitee.com/ygt314159/GeoCalc_3d/releases) 下载打包好的程序即可。

## Windows 用户

Release 里下载由 **Inno Setup** 制作的安装程序：

```
geocalc3d.exe
```

**双击安装**，装完从开始菜单/桌面快捷方式启动即可。

> - 需要 Windows 10/11（64 位），程序使用系统自带的 WebView2 运行时（Windows 10/11 自带）
> - 无需安装 Python 或任何依赖

## WSL2 / Linux 用户

Release 里下载分卷包（Gitee 单附件限制 100MB，产物拆成两个）：

```
GeoCalc3D-wsl2.tar.gz.aa
GeoCalc3D-wsl2.tar.gz.ab
```

**下载到同一目录后合并解压：**

```bash
# 合并两个分卷并解压
cat GeoCalc3D-wsl2.tar.gz.aa GeoCalc3D-wsl2.tar.gz.ab | tar xzf -
cd GeoCalc3D

# 运行（需要 WSLg 图形环境）
export DISPLAY=:0 WAYLAND_DISPLAY=wayland-0
./GeoCalc3D
```

> - 若 WSLg 未开启，先确认 Windows 版本 ≥ Win11 / Win10 21H2，`wsl --update` 后重启
> - 双击运行也可以（如果文件管理器配置了 WSLg 关联）

## 使用说明

1. **添加未知数**：如 `a`（边长）、`t`（参数），可选取值范围
2. **添加点**：填 3 个坐标（可含表达式如 `a`），或设未知数 + 直线/平面约束
   > 提示：3D 中确定一个点通常需要 3 个约束（3 坐标，或坐标+直线组合），前端只提示不强制
3. **添加条件**：表达式相等、线线/线面/面面平行垂直
4. **求解**：输入表达式（如 `AB`、`angABC`、`vABCD`、`dAtpBCD`）→ 🚀 求解
5. **极值探索**：选定表达式（求解结果或自定义）→ 填变量 → 🔍 求驻点
6. **函数值探索**：选定表达式 → 弹框填变量值 → 📊 计算（精确 + 浮点）

### DSL 记号示例

| 记号 | 含义 |
|---|---|
| `AB` | A、B 两点距离 |
| `vecAB` | 向量 AB |
| `angABC` | ∠ABC 角度 |
| `angvABCD` | 向量 AB 与 CD 夹角 |
| `angrABCD` | AB 与平面 CDE 所成角 |
| `angcAB_CDE` | 直线 AB 与平面 CDE 所成角 |
| `dAtpBCD` | A 到平面 BCD 的距离 |
| `vABCD` | 四面体 A-BCD 的体积 |
| `StABC` | 三角形 ABC 面积 |
| `xP` / `yP` / `zP` | 点 P 的坐标 |
| `nABC` | 平面 ABC 的法向量 |

### 示例题目

示例题目不在打包产物内,需要时从仓库获取:

```bash
# 克隆仓库(或单独下载 example_pkl/ 目录)
git clone https://gitee.com/ygt314159/GeoCalc_3d.git
# 应用内"从文件加载"选择 example_pkl/ 下的 .gc.pkl
```

[example_pkl/](example_pkl/) 目录存放示例题目（高考真题改编、个人测试等），说明见 [example_pkl/README.md](example_pkl/README.md)。

---

# 开发（从源码构建）

> 想改代码 / 学习实现？往下看。

## 依赖

- Python（[uv](https://github.com/astral-sh/uv) 管理虚拟环境）
  - **Windows (10/11)**:支持**最新版 Python**(实测 3.14)运行与打包
    —— 使用系统自带 WebView2,零 Qt 依赖,不受 PyQt5 版本限制
  - **WSL2/Linux**:需 **Python 3.12** —— 依赖 PyQt5(5.15.11 无 3.13+ wheel)
- Node.js + npm

## 快速开始

### 后端

```bash
cd backend
uv sync                # 创建 .venv 并安装依赖(sympy/pywebview/PyQt5)
uv run pytest          # 运行全部单元测试
```

### 前端（开发模式，热更新）

```bash
# 终端 1: 前端 dev server
cd frontend && npm install && npm run dev   # http://localhost:9000

# 终端 2: 后端窗口(加载 dev server)
cd backend && DISPLAY=:0 QT_QPA_PLATFORM=xcb .venv/bin/python src/main_dev.py
```

### 正式版（源码运行）

```bash
# 1. 构建前端(输出到 backend/src/ui)
cd frontend && npm run build

# 2. 修正资源路径(Quasar 绝对路径 → file:// 相对路径)
cd backend && .venv/bin/python fix_ui_paths.py

# 3. 启动正式版
cd backend/src && DISPLAY=:0 QT_QPA_PLATFORM=xcb ../.venv/bin/python main.py
```

> 注：GUI 需要图形环境（WSLg 下用 `DISPLAY=:0 QT_QPA_PLATFORM=xcb`）。

## 打包（生成发布产物）

支持 **Windows** 与 **WSL2/Linux**，详细步骤见 [backend/PACKAGING.md](backend/PACKAGING.md)。

### Windows（.exe + 安装包）

```bash
# 1. 构建前端
cd frontend && npm install && npm run build
# 2. PyInstaller 打包(在 Windows 上执行,产物 backend/dist/GeoCalc3D/)
cd backend
uv sync && uv pip install pyinstaller
pyinstaller GeoCalc3D.spec
# 3. (可选)用 Inno Setup 制作安装程序 geocalc3d.exe(见 PACKAGING.md)
```

> Windows 版使用系统自带 WebView2,产物不含 Qt,体积小

### WSL2 / Linux（分卷压缩包）

```bash
# 1-2. 同上构建前端 + PyInstaller 打包(在 WSL2 上执行)
# 3. 分卷压缩(Gitee 单附件限 100MB)
cd backend/dist
tar czf - GeoCalc3D/ | split -b 90m - GeoCalc3D-wsl2.tar.gz.
# 产物: GeoCalc3D-wsl2.tar.gz.aa + .ab,用户合并解压即用
```

> 打包入口只有 `GeoCalc3D.spec`；dist/build 产物不入库，每个开发者按自己的环境打包。

## 测试

```bash
cd backend
uv run pytest                  # 全部测试
uv run pytest tests/           # 只测 src 顶层(problem/sympy)
uv run pytest src/data/tests/  # 只测 data 包
uv run python tests/run_all.py # 集中验证入口
```

详见 [backend/TEST_LAYOUT.md](backend/TEST_LAYOUT.md)。

## 重大版本历史

| 版本 | 说明 |
|---|---|
| v1.0.0 | 正式实现 3D 功能，前后端完整 |
| v1.1.0 | DSL 语法空间体支持（平面/四面体/三棱台等） |
| v1.2.0 | 函数值探索、极值探索上线 |
| v1.3.0 | 向量求解支持 |

## 许可证

[GPL-3.0](LICENSE)，保留原作者署名（本项目为学习用途的 3D 移植）。
