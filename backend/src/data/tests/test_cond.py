"""Cond 条件 + to_raw_latex 美化器 —— 完整测试面

已实现部分(Cond 类):直接测试 ✅
TODO 部分(map_vec_coord / to_raw_latex):契约测试 + xfail
【你实现后:删除 xfail 装饰器即转绿】

覆盖:
  - Cond 初始化(id = raw_latex, eqs 存储)
  - get_raw_latex / get_eqs_latex
  - to_raw_latex 的 DSL 美化规则(2D 规则 + 3D 扩展)
  - map_vec_coord 向量坐标识别
"""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from data.cond import Cond, to_raw_latex, map_vec_coord  # noqa: E402
from sympy import Eq, Symbol  # noqa: E402


class TestCondInit:
    """Cond 初始化(已实现,直接测)"""

    def test_init_sets_id_from_raw_latex(self):
        """id 就是用户原始 LaTeX(天然唯一)"""
        c = Cond(r'AB = CD', [])
        assert c.id == r'AB = CD'

    def test_init_stores_eqs(self):
        """eqs 方程列表被保存"""
        x = Symbol('x')
        eqs = [Eq(x, 1)]
        c = Cond('x = 1', eqs)
        assert c.eqs == eqs
        assert len(c.eqs) == 1

    def test_raw_latex_roundtrip(self):
        """get_raw_latex 返回原始形式"""
        c = Cond(r'AB \parallel CD', [])
        assert c.get_raw_latex() == r'AB \parallel CD'


class TestCondEqsLatex:
    """方程列表 LaTeX 渲染(已实现,但需要 sympy 正常工作)"""

    def test_get_eqs_latex_single(self):
        x = Symbol('x')
        c = Cond('x = 1', [Eq(x, 1)])
        out = c.get_eqs_latex()
        assert '$$' in out
        assert 'x' in out

    def test_get_eqs_latex_multiple(self):
        """多个方程 → 多个 $$ $$ 段"""
        x, y = Symbol('x'), Symbol('y')
        c = Cond('cond', [Eq(x, 1), Eq(y, 2)])
        out = c.get_eqs_latex()
        assert out.count('$$') == 4  # 两个方程,各两个定界符


class TestToRawLatex:
    """用户表达式 → LaTeX 美化契约
    这些规则参照 2D 原版,3D 版你需要补充(见 problem.py 注释)
    """

    @pytest.mark.parametrize('expr, expected_substr', [
        # 2D 原版规则
        ('vecAB', r'\overrightarrow{AB}'),          # 向量箭头
        ('angABC', r'\angle ABC'),                   # 角
        ('ABC', r'\triangle ABC'),                   # 三角形
        ('StABC', 'S_'),                             # 面积下标
        ('xA', r'x_A'),                              # 点坐标下标
        # 3D 新增规则(按你的 DSL 设计,这里给示例)
        # ('VABCD', r'V_{'),                          # 四面体体积
        # ('nABC', r'\vec{n}_{'),                     # 平面法向量
    ])
    def test_rule(self, expr, expected_substr):
        out = to_raw_latex(expr)
        assert expected_substr in out

    def test_deg_to_degree(self):
        """deg → 角度符号"""
        out = to_raw_latex('30deg')
        assert '\\circ' in out or '°' in out


class TestMapVecCoord:
    """向量坐标识别:mark_vec_coord(括号配对) + map_vec_coord(别名映射) 完整链路"""

    def test_mark_2d_coord(self):
        """mark_vec_coord:(1, 2) → Matrix([1, 2])"""
        from vec_parse_utils import mark_vec_coord
        out = mark_vec_coord('(1, 2)')
        assert 'Matrix([1, 2])' in out

    def test_mark_3d_coord(self):
        """mark_vec_coord:(1, 2, 3) → Matrix([1, 2, 3])  ← 3D 新需求"""
        from vec_parse_utils import mark_vec_coord
        out = mark_vec_coord('(1, 2, 3)')
        assert 'Matrix([1, 2, 3])' in out

    def test_mark_4d_coord(self):
        """mark_vec_coord:(1, 2, 3, 4) → 也能处理(算法支持多元组)"""
        from vec_parse_utils import mark_vec_coord
        out = mark_vec_coord('(1, 2, 3, 4)')
        assert 'Matrix([1, 2, 3, 4])' in out

    def test_map_2d_coord(self):
        """map_vec_coord:Matrix([1,2]) → 别名替换,返回映射表"""
        expr, mapping = map_vec_coord('Matrix([1, 2])')
        assert 'Matrix([' not in expr  # 已被别名替换
        assert len(mapping) == 1
        assert 'vec' in expr and 'coord' in expr

    def test_map_3d_coord(self):
        """map_vec_coord:Matrix([1,2,3]) → 别名替换(3D)"""
        expr, mapping = map_vec_coord('Matrix([1, 2, 3])')
        assert 'Matrix([' not in expr
        assert len(mapping) == 1

    def test_full_pipeline_2d(self):
        """完整链路:(1,2) → mark → map → 表达式里无 Matrix"""
        from vec_parse_utils import mark_vec_coord
        marked = mark_vec_coord('(1, 2)')
        expr, _ = map_vec_coord(marked)
        assert 'Matrix([' not in expr

    def test_full_pipeline_3d(self):
        """完整链路:(1,2,3) → mark → map(3D 向量)"""
        from vec_parse_utils import mark_vec_coord
        marked = mark_vec_coord('(1, 2, 3)')
        expr, _ = map_vec_coord(marked)
        assert 'Matrix([' not in expr

