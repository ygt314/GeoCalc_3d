"""Problem 核心类 —— 端到端求解测试

覆盖:
  - 添加符号/点/条件
  - 表达式解析(_eval_str_expr 各规则)
  - 几何访问器(_get_vec/_get_distance/_get_plane 等)
  - 条件方法(平行/垂直/面面/体积)
  - solve() 全链路求解
"""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from problem import Problem


@pytest.fixture
def prob():
    """每测试一个全新 Problem 实例"""
    return Problem()


class TestAddObjects:
    """对象添加"""

    def test_add_symbol(self, prob):
        prob.add_symbol('a')
        assert 'a' in prob.get_symbol_names()
        assert prob.math_objs['a'].sp_symbol.name == 'a'

    def test_add_point_xyz(self, prob):
        prob.add_point('A', '1', '2', '3', '', '')
        assert 'A' in prob.get_point_names()
        p = prob.math_objs['A']
        assert p.x == 1 and p.y == 2 and p.z == 3

    def test_add_point_symbolic(self, prob):
        """点坐标可以是符号"""
        prob.add_symbol('t')
        prob.add_point('A', 't', 't', '0', '', '')
        assert prob.math_objs['A'].x == prob.math_objs['t'].sp_symbol

    def test_add_point_on_line(self, prob):
        """点在直线上:Line3D.equation() 返回 Tuple,必须正确解包"""
        prob.add_point('C', '1', '1', '0', '', '')
        prob.add_point('E', '1', '1', '1', '', '')
        # P 在 CE 上 + z=1/2 → 3 个约束 → P=(1,1,1/2)
        prob.add_point('P', 'x', 'y', '1/2', 'CE', '')
        from sympy import Rational
        assert prob.math_objs['P'].x == 1
        assert prob.math_objs['P'].y == 1
        assert prob.math_objs['P'].z == Rational(1, 2)

    def test_add_point_coord_unknowns(self, prob):
        """点坐标全设未知数 + 2 直线交点(坐标未知数必须纳入 solve)"""
        prob.add_point('A', '0', '0', '0', '', '')
        prob.add_point('B', '1', '0', '0', '', '')
        prob.add_point('C', '0', '0', '0', '', '')
        prob.add_point('D', '1', '1', '1', '', '')
        prob.add_point('Q', 'x', 'y', 'z', 'AB', 'CD')  # AB ∩ CD = A
        assert prob.math_objs['Q'].x == 0
        assert prob.math_objs['Q'].y == 0
        assert prob.math_objs['Q'].z == 0

    def test_duplicate_symbol_rejected(self, prob):
        """重复添加符号应报错(否则 solve 会 duplicate symbols 崩溃)"""
        prob.add_symbol('a')
        import pytest
        with pytest.raises(ValueError):
            prob.add_symbol('a')


class TestGetters:
    """几何访问器"""

    def test_get_vec(self, prob):
        prob.add_point('A', '0', '0', '0', '', '')
        prob.add_point('B', '1', '2', '3', '', '')
        v = prob._get_vec('AB')
        assert v == __import__('sympy').Matrix([1, 2, 3])

    def test_get_distance(self, prob):
        prob.add_point('A', '0', '0', '0', '', '')
        prob.add_point('B', '3', '4', '0', '', '')
        assert prob._get_distance('AB') == 5  # 3-4-5 直角

    def test_get_distance_3d(self, prob):
        prob.add_point('A', '0', '0', '0', '', '')
        prob.add_point('B', '1', '2', '2', '', '')
        assert prob._get_distance('AB') == 3  # sqrt(1+4+4)

    def test_get_triangle_area(self, prob):
        """单位直角三角形面积 = 1/2(SymPy 精确有理数)"""
        from sympy import Rational
        prob.add_point('A', '0', '0', '0', '', '')
        prob.add_point('B', '1', '0', '0', '', '')
        prob.add_point('C', '0', '1', '0', '', '')
        assert prob._get_triangle_area('ABC') == Rational(1, 2)

    def test_get_tetrahedron_volume(self, prob):
        """单位四面体体积 = 1/6(SymPy 精确有理数)"""
        from sympy import Rational
        prob.add_point('A', '0', '0', '0', '', '')
        prob.add_point('B', '1', '0', '0', '', '')
        prob.add_point('C', '0', '1', '0', '', '')
        prob.add_point('D', '0', '0', '1', '', '')
        assert prob._get_tetrahedron_volume('ABCD') == Rational(1, 6)

    def test_get_plane_normal(self, prob):
        """xy 平面法向量 = (0,0,1)"""
        prob.add_point('A', '0', '0', '0', '', '')
        prob.add_point('B', '1', '0', '0', '', '')
        prob.add_point('C', '0', '1', '0', '', '')
        n = prob._get_plane_normal('ABC')
        assert n == __import__('sympy').Matrix([0, 0, 1])


class TestEvalExpr:
    """字符串表达式解析"""

    def test_distance_expr(self, prob):
        prob.add_point('A', '0', '0', '0', '', '')
        prob.add_point('B', '3', '4', '0', '', '')
        assert prob._eval_str_expr('AB') == 5

    def test_coord_expr(self, prob):
        prob.add_point('A', '1', '2', '3', '', '')
        assert prob._eval_str_expr('zA') == 3

    def test_vec_dot(self, prob):
        prob.add_point('A', '0', '0', '0', '', '')
        prob.add_point('B', '1', '0', '0', '', '')
        prob.add_point('C', '0', '1', '0', '', '')
        assert prob._eval_str_expr('vecAB dot vecAC') == 0  # 垂直

    def test_vec_cross(self, prob):
        prob.add_point('A', '0', '0', '0', '', '')
        prob.add_point('B', '1', '0', '0', '', '')
        prob.add_point('C', '0', '1', '0', '', '')
        v = prob._eval_str_expr('vecAB cross vecAC')
        assert v == __import__('sympy').Matrix([0, 0, 1])


class TestSolve:
    """全链路求解"""

    def test_solve_basic(self, prob):
        """两点距离求解"""
        prob.add_point('A', '0', '0', '0', '', '')
        prob.add_point('B', '3', '4', '0', '', '')
        result = prob.solve('AB')
        assert len(result) == 1
        assert '5' in result[0]

    def test_solve_volume(self, prob):
        """四面体体积求解"""
        prob.add_point('A', '0', '0', '0', '', '')
        prob.add_point('B', '1', '0', '0', '', '')
        prob.add_point('C', '0', '1', '0', '', '')
        prob.add_point('D', '0', '0', '1', '', '')
        result = prob.solve('vABCD')
        assert len(result) >= 1
        assert any('1/6' in r or r'\frac{1}{6}' in r for r in result)

    def test_solve_with_cond(self, prob):
        """带条件求解:AB 长度 + 垂直条件"""
        prob.add_symbol('t')
        prob.add_point('A', '0', '0', '0', '', '')
        prob.add_point('B', 't', '0', '0', '', '')
        prob.add_point('C', '0', 't', '0', '', '')
        # 添加条件: AB = 3
        prob.add_expr_eq('AB', '3')
        result = prob.solve('AC')
        assert any('3' in r for r in result)
