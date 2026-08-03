"""测试 MathObj 基类(已实现部分,当前可直接运行)

运行方式:cd backend && .venv/bin/python -m pytest
"""

import sys
from pathlib import Path

# 确保 src 可导入(正常情况下 pyproject.toml 的 pythonpath 配置已处理,
# 这里兜底,方便直接 python 运行时也不报错)
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from data.math_obj import MathObj


class TestMathObj:
    """MathObj 基类的单元测试
    (已经实现,所以这些测试现在就能过)
    """

    def test_init_sets_id(self):
        obj = MathObj('A')
        assert obj.id == 'A'

    def test_init_required_by_empty(self):
        obj = MathObj('cond1')
        assert obj.required_by == set()

    def test_add_required_by(self):
        obj = MathObj('A')
        obj.add_required_by(MathObj('B'))
        assert obj.required_by == {'B'}

    def test_required_by_dedup(self):
        """同一个对象被添加两次依赖,应该只记录一次(set 去重)"""
        obj = MathObj('A')
        b = MathObj('B')
        obj.add_required_by(b)
        obj.add_required_by(b)
        assert obj.required_by == {'B'}


class TestMathObjDependency:
    """依赖图语义测试:验证"被谁依赖"的方向"""

    def test_direction(self):
        """B 依赖 A → A.required_by 包含 B,反过来不成立"""
        a = MathObj('A')
        b = MathObj('B')
        a.add_required_by(b)
        assert 'B' in a.required_by
        assert b.required_by == set()  # B 不"被"任何人依赖
