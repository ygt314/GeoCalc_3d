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

    @pytest.mark.xfail(reason='TODO: 待实现 to_raw_latex', strict=False)
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

    @pytest.mark.xfail(reason='TODO: 待实现 to_raw_latex', strict=False)
    def test_deg_to_degree(self):
        """deg → 角度符号"""
        out = to_raw_latex('30deg')
        assert '\\circ' in out or '°' in out


class TestMapVecCoord:
    """向量坐标识别(2D 三元组 → Matrix,3D 三元组)"""

    @pytest.mark.xfail(reason='TODO: 待实现 map_vec_coord', strict=False)
    def test_mark_2d_coord(self):
        """(1, 2) → Matrix([1, 2])"""
        expr, mapping = map_vec_coord('vec(1, 2)')
        assert 'Matrix([' in expr

    @pytest.mark.xfail(reason='TODO: 待实现 map_vec_coord', strict=False)
    def test_mark_3d_coord(self):
        """(1, 2, 3) → Matrix([1, 2, 3])  ← 3D 新需求"""
        expr, mapping = map_vec_coord('(1, 2, 3)')
        assert 'Matrix([' in expr
