# 3D 前端适配方案(M5)

> 目标:复制 2D 前端脚手架,改为 3D 版(加 z 坐标 + 3D 条件按钮)。
> 原则:条件按钮与后端方法一一对应,全等/相似**不支持**(立体几何少用,2D 专属)。

## 一、脚手架

```bash
cd ~/ai_home/GeoCalc_3d
cp -r ~/GeometryCalculator/frontend/ frontend/   # 复制 2D 底子
cd frontend && rm -rf node_modules .quasar dist   # 清掉 2D 产物
# 改 package.json: name → geocalc-3d-frontend, productName → 3D几何计算器 前端
# 改 index.html: title 等
npm install   # 或 pnpm install(2D 用 pnpm)
```

## 二、前端改动点(与 2D 差异)

### 1. AddPoint.vue —— 加竖坐标

```
横坐标(x_str) | 纵坐标(y_str) | 竖坐标(z_str) ← 新增
在直线/平面 1(line1) | 在直线/平面 2(line2)

提交: window.pywebview.api.problem.add_point(name, x_str, y_str, z_str, line1, line2)
校验: 3 个坐标中恰好 2 个非空(x/y/z 任一可留空设未知数)
```

### 2. AddCondsAll.vue —— 3D 条件按钮

| 按钮 | relOp | 后端方法 | 校验 |
|---|---|---|---|
| 表达式相等 | `=` | `add_expr_eq` | 两表达式非空 |
| 两直线平行 | `\parallel` | `add_line_parallel_line` | 两个两点线名 |
| 两直线垂直 | `\perp` | `add_line_perp_line` | 两个两点线名 |
| 线面平行 | `\parallel` | `add_line_parallel_plane` | 两点线 + 三点面 |
| 线面垂直 | `\perp` | `add_line_perp_plane` | 两点线 + 三点面 |
| 面面平行 | `\parallel` | `add_plane_parallel_plane` | 两个三点面 |
| 面面垂直 | `\perp` | `add_plane_perp_plane` | 两个三点面 |

**不提供**:三角形全等/相似(立体几何少用,平面判断,去 2D 版)。

### 3. validityCheck.ts —— 新增校验

```
isValidLineName: 两点线名(如 AB)
isValidPlaneName: 三点面名(如 ABC)
线面组合校验: 线(2点) + 面(3点)
```

### 4. Solve.vue —— 基本不动

DSL 表达式(vABCD/angrABCD/dAtpBCD 等)直接喂 `problem.solve()`,
KaTeX 渲染 to_raw_latex 输出。加"极值探索"按钮(M6 预留)。

## 三、跑起来

```bash
# 终端 1: 前端 dev server
cd frontend && npm run dev        # 起 9000 端口

# 终端 2: 后端窗口
cd backend && .venv/bin/python src/main_dev.py   # pywebview 加载 9000
```

## 四、注意(踩坑参考)

- 2D 前端用 PyQt5(Chromium 87)会崩 `Object.hasOwn`,3D 后端若用 PyQt6 则无此问题
  (当前 venv 是 pywebview 默认,若用 GTK 后端则完全没这问题)
- pywebview js_api 桥接:前端 `window.pywebview.api.problem.xxx` 直接调用
