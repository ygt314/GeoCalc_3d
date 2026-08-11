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
| 后端 | Python 3.12 + SymPy（符号计算）+ pywebview |
| GUI | PyQt5 / QtWebEngine（Chromium 87） |
| 前端 | Quasar (Vue 3) + KaTeX（公式渲染） |
| 测试 | pytest（81 个单元测试全绿） |

## 快速开始

### 依赖

- Python 3.12（[uv](https://github.com/astral-sh/uv) 管理虚拟环境）
- Node.js + npm

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

### 正式版（打包构建）

```bash
# 1. 构建前端(输出到 backend/src/ui)
cd frontend && npm run build

# 2. 修正资源路径(Quasar 绝对路径 → file:// 相对路径)
cd backend && .venv/bin/python fix_ui_paths.py

# 3. 启动正式版
cd backend/src && DISPLAY=:0 QT_QPA_PLATFORM=xcb ../.venv/bin/python main.py
```

> 注：GUI 需要图形环境（WSLg 下用 `DISPLAY=:0 QT_QPA_PLATFORM=xcb`）。

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

## 测试

```bash
cd backend
uv run pytest                  # 全部测试
uv run pytest tests/           # 只测 src 顶层(problem/sympy)
uv run pytest src/data/tests/  # 只测 data 包
uv run python tests/run_all.py # 集中验证入口
```

详见 [backend/TEST_LAYOUT.md](backend/TEST_LAYOUT.md)。

## 示例题目

`backend/2025GC1.gc.pkl` 是一道示例题（空间点 O 到多点等距求坐标），应用内"从文件加载"即可体验，说明见 [backend/2025GC1.example.md](backend/2025GC1.example.md)。

## 许可证

[GPL-3.0](LICENSE)，保留原作者署名（本项目为学习用途的 3D 移植）。
