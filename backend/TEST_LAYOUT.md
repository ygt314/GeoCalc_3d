# 后端测试布局

## 目录职责

```
backend/
├── tests/                  ← 管 src 顶层模块
│   ├── conftest.py         ← pytest 配置说明
│   ├── test_problem.py     ← Problem 核心类(16 个端到端测试)
│   ├── test_sympy_3d.py    ← SymPy 3D 数学地基(9 个)
│   └── run_all.py          ← 集中验证脚本(汇总两处测试)
│
└── src/
    └── data/
        └── tests/          ← 管 data 包(cond/math_obj/point/symbol)
            ├── __init__.py ← 必须(包内测试目录)
            ├── conftest.py
            ├── test_cond.py       (18 个)
            ├── test_math_obj.py   (9 个)
            ├── test_point.py      (4 个)
            └── test_symbol.py     (12 个)
```

## 命令

```bash
cd backend

# 分层跑: 只跑顶层(problem/sympy 地基)
uv run pytest tests/

# 分层跑: 只跑 data 包
uv run pytest src/data/tests/

# 集中验证: 一条命令跑全部(推荐,CI 用这个)
uv run python tests/run_all.py
uv run python tests/run_all.py -v       # 详细
uv run python tests/run_all.py -k cond  # 过滤

# 等价的全量命令
uv run pytest
```

## 原则

1. **tests/ 不管子目录** —— data 包的测试归属 data/tests,不混进来
2. **data/tests 只管 data/** —— 不测 problem.py
3. **分层价值** —— 修改某层时,只跑对应层快速验证;全量由 run_all 兜底
4. 修改 src 顶层(如 problem.py)后至少跑 `uv run pytest tests/`;
   修改 data 包后跑 `uv run pytest src/data/tests/`
