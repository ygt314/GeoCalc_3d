"""MathObj 抽象基类 —— 完整测试面(已实现,全部通过)

覆盖:
  - 初始化(id / required_by)
  - 依赖关系语义(add_required_by / 去重 / 方向性)
  - 与子类(符号/点/条件)的协作
"""

import sys
from pathlib import Path

# 确保 src 可导入(pyproject 的 pythonpath 已配,这里兜底)
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from data.math_obj import MathObj


class TestInit:
    """初始化"""

    def test_init_sets_id(self):
        obj = MathObj('A')
        assert obj.id == 'A'

    def test_init_required_by_empty(self):
        obj = MathObj('cond1')
        assert obj.required_by == set()

    def test_id_is_any_string(self):
        """id 可以是任意字符串(包括 LaTeX 形式)"""
        obj = MathObj(r'$$ AB = CD $$')
        assert obj.id == r'$$ AB = CD $$'


class TestRequiredBy:
    """依赖关系:required_by = 被谁依赖"""

    def test_add_required_by(self):
        obj = MathObj('A')
        obj.add_required_by(MathObj('B'))
        assert obj.required_by == {'B'}

    def test_add_multiple(self):
        obj = MathObj('A')
        obj.add_required_by(MathObj('B'))
        obj.add_required_by(MathObj('C'))
        assert obj.required_by == {'B', 'C'}

    def test_dedup(self):
        """同一依赖添加两次只记一次(set 天然去重)"""
        obj = MathObj('A')
        b = MathObj('B')
        obj.add_required_by(b)
        obj.add_required_by(b)
        assert obj.required_by == {'B'}

    def test_direction(self):
        """方向性:B 依赖 A → A.required_by 含 B;A 不依赖 B"""
        a = MathObj('A')
        b = MathObj('B')
        a.add_required_by(b)
        assert 'B' in a.required_by
        assert b.required_by == set()  # B 没有被任何人依赖


class TestSubclassContract:
    """子类契约:MathObj 作为 ABC,子类必须能正常继承"""

    def test_subclass_init(self):
        """子类调用 super().__init__(id) 后继承 id 和 required_by"""
        class FakeObj(MathObj):
            pass

        obj = FakeObj('fake')
        assert obj.id == 'fake'
        assert obj.required_by == set()

    def test_chain_dependency(self):
        """链式依赖:A ← B ← C(C 依赖 B,B 依赖 A)"""
        a, b, c = MathObj('A'), MathObj('B'), MathObj('C')
        a.add_required_by(b)   # B 依赖 A
        b.add_required_by(c)   # C 依赖 B
        assert 'B' in a.required_by
        assert 'C' in b.required_by
