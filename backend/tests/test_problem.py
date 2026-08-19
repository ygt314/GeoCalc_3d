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

    def test_point_in_plane(self, prob):
        """点在平面: P(全未知) ∈ pABC → zP=0 被约束"""
        prob.add_point('A', '0', '0', '0', '', '')
        prob.add_point('B', '1', '0', '0', '', '')
        prob.add_point('C', '1', '1', '0', '', '')
        prob.add_point('P', 'x', 'y', 'z', '', '')   # 全未知
        prob.add_point_in_plane('P', 'pABC')         # 必须带 p 前缀
        result = prob.solve('zP')
        assert any('z_P = 0' in r for r in result)

    def test_point_in_plane_requires_p(self, prob):
        """点在平面: 平面名必须带 p 前缀(裸 ABC 会报错)"""
        prob.add_point('A', '0', '0', '0', '', '')
        prob.add_point('B', '1', '0', '0', '', '')
        prob.add_point('C', '1', '1', '0', '', '')
        prob.add_point('P', 'x', 'y', 'z', '', '')
        import pytest
        # 裸 ABC: _get_plane_normal('ABC') 取 name[1:4]='BC'(长度不足)→ 报错
        with pytest.raises(Exception):
            prob.add_point_in_plane('P', 'ABC')


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
        """xy 平面法向量 = (0,0,1)（平面语法: pABC 或 ABCD）"""
        prob.add_point('A', '0', '0', '0', '', '')
        prob.add_point('B', '1', '0', '0', '', '')
        prob.add_point('C', '0', '1', '0', '', '')
        prob.add_point('D', '1', '1', '0', '', '')
        n = prob._get_plane_normal('pABC')
        assert n == __import__('sympy').Matrix([0, 0, 1])
        # 四点形式 ABCD: 后端取 name[1:4]=BCD,法向量可能反向
        # (法向量反向仍是同一平面,平行/垂直判断不受影响)
        n2 = prob._get_plane_normal('ABCD')
        assert n2 == __import__('sympy').Matrix([0, 0, -1])


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


class TestExplore:
    """极值点探索(双入口: solve 求解 + expore_extrema 探索)

    expore_extrema(choice, sym_str, custom):
      - custom=True  → choice 是自定义表达式字符串(DSL 解析)
      - custom=False → choice 是 solve 结果缓存的 LaTeX 键
    """

    def _solve_first(self, prob, expr: str):
        """求解并把第一个结果作为缓存键返回"""
        prob.solve(expr)
        return next(iter(prob._last_exprs))

    def test_custom_expr(self, prob):
        """自定义表达式: u²+v² 的驻点是 (0,0), 函数值 0 → (0,0,0)"""
        prob.add_symbol('u')
        prob.add_symbol('v')
        result = prob.expore_extrema('u**2 + v**2', 'u v', custom=True)
        assert '(0,0,0)' in result

    def test_solution_key(self, prob):
        """用求解结果: AB=2 解出 t=±2, 探索常数无驻点(返回空集)"""
        prob.add_symbol('t')
        prob.add_point('A', '0', '0', '0', '', '')
        prob.add_point('B', 't', '0', '0', '', '')
        prob.add_expr_eq('AB', '2')
        prob.solve('t')
        assert prob._last_exprs  # 有解缓存
        key = next(iter(prob._last_exprs))
        result = prob.expore_extrema(key, 't', custom=False)
        assert result == ['\\emptyset']  # 常数解无驻点

    def test_custom_dsl(self, prob):
        """自定义表达式支持 DSL 记号: AB² 关于 t 的驻点 (0, 函数值0)"""
        prob.add_symbol('t')
        prob.add_point('A', '0', '0', '0', '', '')
        prob.add_point('B', 't', '0', '0', '', '')
        result = prob.expore_extrema('AB**2', 't', custom=True)
        assert '(0,0)' in result

    def test_json_serializable(self, prob):
        """返回必须能 JSON 序列化(pywebview 桥接要求)"""
        import json
        prob.add_symbol('u')
        prob.add_symbol('v')
        result = prob.expore_extrema('u**2 + v**2', 'u v', custom=True)
        json.dumps(result)  # 不抛异常即通过


class TestExploreFunc:
    """函数值探索: 给定变量值,算函数值(精确+浮点双显示)"""

    def test_custom(self, prob):
        """自定义表达式: t²-2t+1 @ t=2 → $ 1 = 1$"""
        prob.add_symbol('t')
        result = prob.expore_func('t**2 - 2*t + 1', {'t': 2}, custom=True)
        assert '1' in result

    def test_min_point(self, prob):
        """最小值点: t²-2t+1 @ t=1 → $ 0 = 0$"""
        prob.add_symbol('t')
        result = prob.expore_func('t**2 - 2*t + 1', {'t': 1}, custom=True)
        assert '0' in result

    def test_fraction(self, prob):
        """分数值: 1/t @ t=2 → $ \\frac{1}{2} = 0.5$"""
        prob.add_symbol('t')
        result = prob.expore_func('1/t', {'t': 2}, custom=True)
        assert r'\frac{1}{2}' in result  # 精确 latex
        assert '0.5' in result           # 浮点

    def test_solution_key(self, prob):
        """用求解结果缓存键"""
        prob.add_symbol('t')
        prob.add_point('A', '0', '0', '0', '', '')
        prob.add_point('B', 't', '0', '0', '', '')
        prob.add_expr_eq('AB', '2')
        prob.solve('AB')
        assert prob._last_exprs
        key = next(iter(prob._last_exprs))
        # AB=2 解出 t=±2, 求 f(AB)=2 @ t=2 → 2
        result = prob.expore_func(key, {'t': 2}, custom=False)
        assert '2' in result

    # ── 嵌套根号化简(sqrtdenest)──
    # 参考原版 issue: https://github.com/zhdbk3/GeometryCalculator/issues/5

    def test_solve_sqrtdenest(self, prob):
        """求解: √(3+2√2) 化简为 1+√2"""
        result = prob.solve('sqrt(3 + 2*sqrt(2))')
        # solve 返回 '√(3+2√2) = 1+√2'
        assert any('1 + \\sqrt{2}' in r for r in result)

    def test_extrema_sqrtdenest(self, prob):
        """极值: t²-2√3·t+1 驻点含 √3"""
        prob.add_symbol('t')
        result = prob.expore_extrema('t**2 - 2*sqrt(3)*t + 1', 't', custom=True)
        assert any(r'\sqrt{3}' in r for r in result)

    def test_func_sqrtdenest(self, prob):
        """函数值: t² @ t=1+√2 保留精确根号 + 浮点"""
        prob.add_symbol('t')
        result = prob.expore_func('t**2', {'t': '1 + sqrt(2)'}, custom=True)
        assert '\\sqrt{2}' in result  # 精确 latex 含根号
        assert '5.82843' in result    # 浮点近似

    # ── 部分代入(新行为): 只代入部分变量,未代入的保留为符号 ──

    def test_partial_substitution(self, prob):
        """部分代入: t²+u @ t=2 → u 保留为符号"""
        prob.add_symbol('t')
        prob.add_symbol('u')
        result = prob.expore_func('t**2 + u', {'t': 2}, custom=True)
        assert 'u' in result        # 未代入的 u 保留
        assert '4' in result        # t² 已代入

    def test_no_substitution(self, prob):
        """不代入: t²+u @ {} → 全部保留为符号"""
        prob.add_symbol('t')
        prob.add_symbol('u')
        result = prob.expore_func('t**2 + u', {}, custom=True)
        assert 'u' in result
        assert 't' in result

    def test_partial_dsl(self, prob):
        """DSL + 部分代入: AB² @ t=1 → 完全确定"""
        prob.add_symbol('t')
        prob.add_point('A', '0', '0', '0', '', '')
        prob.add_point('B', 't', '0', '0', '', '')
        result = prob.expore_func('AB**2', {'t': 1}, custom=True)
        assert '1' in result

    def test_partial_still_json(self, prob):
        """部分代入结果仍可 JSON 序列化"""
        import json
        prob.add_symbol('t')
        prob.add_symbol('u')
        result = prob.expore_func('t**2 + u', {'t': 2}, custom=True)
        json.dumps(result)  # 不抛异常即通过
