"""3D几何计算器 - 全量测试集中验证脚本

职责: 一条命令跑完所有测试(backend/tests + src/data/tests)。

用法:
    cd backend
    uv run python tests/run_all.py          # 跑全部
    uv run python tests/run_all.py -v       # 详细模式
    uv run python tests/run_all.py -k cond  # 过滤

说明:
    backend/tests/        → 管 src 顶层(problem.py、sympy 地基)
    backend/src/data/tests/ → 管 data 包(cond/math_obj/point/symbol)
    本脚本调用 pytest 收集上述两处,等价于 `uv run pytest`。
"""

import subprocess
import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).parent.parent
# 传给 pytest 的额外参数(如 -v、-k xxx)
extra_args = sys.argv[1:]

# 两个测试目录
test_targets = [
    str(BACKEND_DIR / 'tests'),
    str(BACKEND_DIR / 'src' / 'data' / 'tests'),
]

print('=' * 60)
print('3D几何计算器 全量测试')
print('  顶层 tests/:            {}'.format(test_targets[0]))
print('  data 包 tests/:         {}'.format(test_targets[1]))
print('=' * 60)

cmd = [sys.executable, '-m', 'pytest', *test_targets, *extra_args]
result = subprocess.run(cmd, cwd=str(BACKEND_DIR))

print('=' * 60)
if result.returncode == 0:
    print('✅ 全部测试通过')
else:
    print('❌ 存在失败测试(exit={})'.format(result.returncode))
print('=' * 60)
sys.exit(result.returncode)
