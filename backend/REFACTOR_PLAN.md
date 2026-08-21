# problem.py 拆分计划(REFACTOR_PLAN)

> 现状: `problem.py` 771 行,单文件承载全部逻辑(工具函数/装饰器/几何访问器/DSL/条件/查询/求解/探索)。
> 目标: 按职责拆成 5 个模块,`Problem` 类本身保持单一入口(其他模块通过 mixin 方式挂到 Problem)。

## 一、拆分方案

| 新文件 | 内容(从 problem.py 迁出) | 原行号 | 职责 |
|---|---|---|---|
| `src/geo_tools.py` | `expr_to_list`、`get_ans`、`track_requirement` 装饰器、`AddCond/AddBinCond/AddUnaryCond` | 49-133 | 通用工具 + 条件装饰器 |
| `src/geo_accessors.py` | `_get_sp_symbol`~`_get_Ss_volume`(访问器)+ `_eval_str_expr`(DSL 解析) | 167-360 | 几何访问器 + DSL 规则表 |
| `src/geo_objects.py` | `add_symbol`、`add_O_point`、`add_point*`、`add_*_cond`(条件方法) | 399-568 | 对象与条件添加 |
| `src/geo_query.py` | `get_*` 查询、`del_objs`、`save/load` | 570-677 | 查询/删除/存取 |
| `src/geo_solve.py` | `_get_target`、`solve`、`solve_vec`、`solve_mult`、`expore_*` | 678-771 | 求解 + 探索 |

**Problem 类的组装方式(两选一):**
- 方案 A(mixin): `class Problem(GeoAccessors, GeoObjects, GeoQuery, GeoSolve):` —— 各模块定义带方法的部分类
- 方案 B(组合): `Problem` 持有各子对象 —— 改动大,不推荐

**推荐方案 A**: 方法保持 `self` 直调,前端调用 `problem.xxx` 不变,`api.py` 零改动。

## 二、拆分原则

1. **`__init__` 和 `_add_math_obj`/`add_cond` 留在 problem.py 本体**(最核心的状态管理)
2. 各模块只依赖 `problem.py` 的类型定义(`MathObj`/`Cond` 等来自 data 包),不循环导入
3. `_eval_str_expr` 的 DSL 规则表(最大的一块,~70 行)随 accessors 走
4. 拆完后 `problem.py` 本体只剩: imports + 5 个 mixin 声明 + `__init__` + 状态方法(~150 行)

## 三、风险与对策

| 风险 | 对策 |
|---|---|
| 循环导入(模块间互相引用) | 单向依赖: tools ← accessors ← objects ← query ← solve, Problem 最后组装 |
| mixin 方法名冲突 | 各模块方法名前缀/职责互斥(已按章节分界,无重叠) |
| `_eval_str_expr` 依赖 `_get_*` 访问器 | 同模块内解决(accessors 包含两者) |
| 重构引入行为差异 | **契约测试兜底**(见下),全部跑绿才算完成 |

## 四、验证步骤

1. `uv run pytest` 全量绿(87 passed)
2. 启动 `main.py` 手动回归: 添加点/条件 → 求解 → 极值 → 函数值
3. `problem.py` 行数从 771 → ~150(本体)

---
*本计划仅文档,不实施。实施时按此执行,每拆一个模块跑一次测试。*
