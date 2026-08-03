# 3D几何计算器 — 开发蓝图

> 学习项目,原型:[着火的冰块nya] 的 [GeometryCalculator](https://github.com/zhdbk3/GeometryCalculator)(GPL-3.0)
> 目标:暴力计算立体几何。本文件是学习+开发的路线图,随开发进度更新。

## 一、项目定位

| | 2D 原版 | 3D 版(本仓库) |
|---|---|---|
| 坐标系 | 平面 (x, y) | 空间 (x, y, z) |
| 基本对象 | 点、线 | 点、线、**平面**、四面体 |
| 核心引擎 | SymPy solve 联立方程 | 同左(不变) |
| 输入 DSL | `AB` `vecAB` `angABC` `StABC` | 继承 + `zA` `VABCD` `nABC` 等 |

**核心思想(原版精髓,必须吃透):**
一切几何关系 → 代数方程 → SymPy 暴力求解。
"暴力"不是算法暴力,而是**把几何翻译成代数后让计算机硬解**。

## 二、代码地图

```
backend/src/
├── main_dev.py        # pywebview 入口(加载 localhost:9000)
├── api.py             # 桥接层:前端 JS ↔ Python(单例 API)
├── logger.py          # 日志(前端/后端两个 logger)
├── type_hints.py      # TypedDict 类型
├── vec_parse_utils.py # mark_vec_coord + Infix/dot 中缀运算符
├── problem.py         # ★ 核心:Problem 类(对象管理/DSL/条件/求解)
└── data/
    ├── math_obj.py    # MathObj 抽象基类(id + required_by 依赖图)
    ├── symbol.py      # GCSymbol 未知数(含取值范围→SymPy 假设)
    ├── point.py       # GCPoint 点(3D: x, y, z + Point3D)
    └── cond.py        # Cond 条件(raw_latex + eqs)+ to_raw_latex 美化器
```

## 三、学习顺序(对照 2D 原版阅读)

| 步骤 | 文件 | 重点 | 3D 改动量 |
|---|---|---|---|
| 1 | `problem.py` 的 `solve()` | 求解整体流程 | 极小 |
| 2 | `problem.py` 的 `_eval_str_expr()` | 正则规则表 DSL | **大**(扩展规则) |
| 3 | `problem.py` 的条件方法 | 几何→方程翻译 | **大**(新增类型) |
| 4 | `data/symbol.py` | 取值范围→SymPy 假设 | 无 |
| 5 | `data/point.py` | 3D 坐标 | 小 |
| 6 | `data/cond.py` 的 `to_raw_latex()` | LaTeX 美化规则 | 中(加规则) |
| 7 | `data/math_obj.py` | 依赖图 | 无 |
| 8 | `vec_parse_utils.py` | 中缀 dot 魔法 | 小 |

## 四、2D → 3D 数学转换速查

### 距离
- 空间两点:√((x₁-x₂)² + (y₁-y₂)² + (z₁-z₂)²)
- 点面距:|ax₀+by₀+cz₀+d| / √(a²+b²+c²) ← 平面方程 Ax+By+Cz+D=0

### 向量
- 3D 向量:Matrix([dx, dy, dz])
- 点积:u·v(夹角公式同 2D)
- **叉积** u×v:垂直向量 ← 3D 新武器,平行判断靠它
- 混合积 (u×v)·w:体积/共面判断 ← 3D 新武器

### 直线(3D 表示)
- 2D:y = kx + b(有斜率)
- 3D:参数式 P = P₀ + t·d(点 + 方向向量)或两平面交线
- 方向向量 d = (x₂-x₁, y₂-y₁, z₂-z₁)

### 平面(3D 新增)
- 一般式:Ax + By + Cz + D = 0
- 法向量 n = (A, B, C)
- 由三点确定:Plane(p1, p2, p3),法向量 = 两向量叉积

### 平行/垂直(全用向量判定)
| 关系 | 判定 |
|---|---|
| 线∥线 | 方向向量叉积 = 0 |
| 线⊥线 | 方向向量点积 = 0 |
| 线∥面 | 方向·法 = 0 |
| 线⊥面 | 方向 ∥ 法(叉积 = 0) |
| 面∥面 | 法向量叉积 = 0 |
| 面⊥面 | 法向量点积 = 0 |

### 体积/面积
- 三角形面积(空间):|AB × AC| / 2
- 四面体体积:|AB·(AC×AD)| / 6(混合积绝对值)

## 五、开发里程碑

- [ ] **M1 骨架跑通**:后端代码结构 + venv 依赖 + solve 空转(只解表达式相等)
- [ ] **M2 DSL 基础**:AB 距离 / vecAB / zA 坐标 / angABC 能解析
- [ ] **M3 核心条件**:线线平行垂直、线面、面面、共面、点面距
- [ ] **M4 特殊对象**:四面体体积、二面角、平面方程
- [ ] **M5 LaTeX + 前端**:to_raw_latex 美化 + Quasar 前端适配(加 z 输入框)
- [ ] **M6 打包**(可选):Nuitka 打包(参照原版)

## 六、注意点(踩坑记录)

1. **前端兼容性**:若用 PyQt5(Chromium 87),Quasar 会崩 `Object.hasOwn`。
   3D 版直接用 PyQt6 规避,或在 index.html 加 polyfill(原版已踩过)。
2. **3D 直线不能表示成单一方程**:原版 `_get_line().equation()` 返回 Ax+By+C=0,
   3D 直线需要参数式或两平面方程,求解时要注意。
3. **"平行四边形"在 3D 的坑**:四个点可能不共面,需要先证共面或换判定法。
4. **SymPy 的 solve 对三维方程组可能很慢**:先用小例子测通再上复杂题。
5. **GPL-3.0 合规**:本仓库使用与原作者相同的 GPL-3.0 协议,保留署名(已在 README 标注)。
