"""problem.py 拆分契约测试(REFACTOR_PLAN 配套)

这些测试锁定 problem.py 各职责模块的行为,是拆分的"安全网":
- 模块契约测试(xfail): 拆分尚未实施,实施后 XPASS → 删标记转正
- 工具函数测试(已转正): expr_to_list/get_ans 已是独立函数,无需拆分

分组对应 REFACTOR_PLAN.md 的 5 个新文件:
- TestGeoToolsContract   → geo_tools.py (工具/装饰器)
- TestAccessorsContract  → geo_accessors.py (访问器 + DSL)
- TestObjectsContract    → geo_objects.py (点/条件添加)
- TestQueryContract      → geo_query.py (查询/存取)
- TestSolveContract      → geo_solve.py (求解/探索)

用法: uv run pytest tests/test_refactor_contract.py
"""
import pytest
from problem import Problem


@pytest.fixture
def prob():
    """每测试一个全新 Problem 实例"""
    return Problem()

# ═══════════════════════════════════════════════════════
# 1. geo_tools.py: 工具函数与装饰器
# ═══════════════════════════════════════════════════════
class TestGeoToolsContract:
    def test_expr_to_list_scalar(self):
        """expr_to_list: 标量 → [自身]"""
        from problem import expr_to_list
        from sympy import sqrt
        assert expr_to_list(sqrt(2)) == [sqrt(2)]

    def test_expr_to_list_matrix(self):
        """expr_to_list: Matrix → 坐标列表"""
        from problem import expr_to_list
        from sympy import Matrix
        assert expr_to_list(Matrix([1, 2, 3])) == [1, 2, 3]

    def test_expr_to_list_immutable(self):
        """expr_to_list: ImmutableDenseMatrix 也能识别(向量)"""
        from problem import expr_to_list
        from sympy import Matrix
        im = Matrix([1, 2, 3]).as_immutable()
        assert expr_to_list(im) == [1, 2, 3]

    def test_expr_to_list_choice(self):
        """expr_to_list: choice='expr'/'matrix' 分流"""
        from problem import expr_to_list
        from sympy import Matrix
        m = Matrix([1, 2, 3])
        assert expr_to_list(m, 'expr') == []
        assert expr_to_list(m, 'matrix') == [1, 2, 3]

    def test_get_ans_modes(self):
        """get_ans: b=1 只 simplify, b=2 只 sqrtdenest, 默认都做"""
        from problem import get_ans
        from sympy import sqrt, simplify, sqrtdenest
        x = sqrt(3 + 2 * sqrt(2))
        assert get_ans(x, 1) == simplify(x)
        assert get_ans(x, 2) == sqrtdenest(x)

    def test_track_requirement_decorator(self):
        """track_requirement: 访问点时记录依赖"""
        from problem import Problem
        p = Problem()
        p.add_point('A', '0', '0', '0', '', '')
        p.add_point('B', '1', '0', '0', '', '')
        # 求解 AB 会访问 A、B → tracker 记录这两个点
        p.solve('AB')
        assert len(p.requirements_tracker) == 2

    def test_add_bin_cond_raw_latex(self):
        """AddBinCond: 条件添加(非恒成立场景)"""
        from problem import Problem
        p = Problem()
        p.add_point('A', '0', '0', '0', '', '')
        p.add_point('B', '1', '0', '0', '', '')
        p.add_point('C', 'x', '1', '0', '', '')   # 参数点,AB=AC 非恒成立
        p.add_expr_eq('AB', 'AC')  # 不抛异常即通过
        assert len(p.cond_ids) == 1

# ═══════════════════════════════════════════════════════
# 2. geo_accessors.py: 几何访问器 + DSL 解析
# ═══════════════════════════════════════════════════════
@pytest.mark.xfail(reason="REFACTOR_PLAN: 模块未拆(暂缓),实现后转正")
class TestAccessorsContract:
    def test_get_x_of(self, prob):
        """_get_x_of: 取点 x 坐标"""
        prob.add_point('A', '1', '2', '3', '', '')
        assert prob._get_x_of('A') == 1

    def test_get_vec(self, prob):
        """_get_vec: 方向向量"""
        prob.add_point('A', '0', '0', '0', '', '')
        prob.add_point('B', '1', '2', '3', '', '')
        assert list(prob._get_vec('AB')) == [1, 2, 3]

    def test_get_plane_normal_p(self, prob):
        """_get_plane_normal: pABC → 法向量"""
        prob.add_point('A', '0', '0', '0', '', '')
        prob.add_point('B', '1', '0', '0', '', '')
        prob.add_point('C', '0', '1', '0', '', '')
        # A→B→C 顺序得出 +z 法向量 (0,0,1)
        assert list(prob._get_plane_normal('pABC')) == [0, 0, 1]

    def test_eval_str_dot(self, prob):
        """DSL: dot 点积"""
        prob.add_point('A', '1', '0', '0', '', '')
        prob.add_point('B', '0', '1', '0', '', '')
        assert prob._eval_str_expr('vecAB dot vecAB') == 2

    def test_eval_str_cross(self, prob):
        """DSL: cross 叉积"""
        prob.add_point('A', '1', '0', '0', '', '')
        prob.add_point('B', '0', '1', '0', '', '')
        r = prob._eval_str_expr('vecAB cross vecAB')
        assert list(r) == [0, 0, 0]

    def test_eval_str_volume(self, prob):
        """DSL: vABCD 四面体体积"""
        prob.add_point('A', '0', '0', '0', '', '')
        prob.add_point('B', '1', '0', '0', '', '')
        prob.add_point('C', '0', '1', '0', '', '')
        prob.add_point('D', '0', '0', '1', '', '')
        assert prob._eval_str_expr('vABCD') != 0

# ═══════════════════════════════════════════════════════
# 3. geo_objects.py: 对象与条件添加
# ═══════════════════════════════════════════════════════
@pytest.mark.xfail(reason="REFACTOR_PLAN: 模块未拆(暂缓),实现后转正")
class TestObjectsContract:
    def test_add_symbol(self, prob):
        """add_symbol: 添加符号"""
        prob.add_symbol('a')
        assert 'a' in prob.symbol_names

    def test_add_O_point(self, prob):
        """add_O_point: 原点"""
        prob.add_O_point('O')
        assert prob.math_objs['O'].get_latex() == 'O \\left( 0, 0, 0 \\right)'

    def test_add_point_from_move(self, prob):
        """add_point_from_move: 平移加点"""
        prob.add_point('A', '1', '2', '3', '', '')
        prob.add_point_from_move('B', 'xA+1')
        assert prob.math_objs['B'].get_latex() == 'B \\left( 2, 2, 3 \\right)'

    def test_add_point_from_vec(self, prob):
        """add_point_from_vec: 向量指点"""
        prob.add_point('A', '1', '2', '3', '', '')
        prob.add_point('B', '4', '6', '8', '', '')
        prob.add_point_from_vec('C', 'A', 'vecAB')
        assert prob.math_objs['C'].get_latex() == 'C \\left( 4, 6, 8 \\right)'

    def test_add_line_parallel_plane(self, prob):
        """add_line_parallel_plane: 线面平行(方向含参数,有条件)"""
        prob.add_point('A', '0', '0', '0', '', '')
        prob.add_point('B', '1', '0', '0', '', '')
        prob.add_point('C', '0', '1', '0', '', '')
        # 线 PQ: P(0,0,a), Q(1,1,b) → 方向 (1,1,b-a)
        # 与 z=0 面法向量(0,0,1)点积 = b-a,平行需要 b=a(有条件)
        prob.add_symbol('a')
        prob.add_symbol('b')
        prob.add_point('P', '0', '0', 'a', '', '')
        prob.add_point('Q', '1', '1', 'b', '', '')
        prob.add_line_parallel_plane('PQ', 'pABC')
        assert len(prob.cond_ids) == 1

# ═══════════════════════════════════════════════════════
# 4. geo_query.py: 查询 / 删除 / 存取
# (DataOperate 父类已实现,本组已转正)
# ═══════════════════════════════════════════════════════
class TestQueryContract:
    def test_get_point_names(self, prob):
        """get_point_names"""
        prob.add_point('A', '0', '0', '0', '', '')
        assert 'A' in prob.get_point_names()

    def test_get_orig_point(self, prob):
        """get_orig_point: 空→'';add_O_point 后→名称"""
        assert prob.get_orig_point() == ''
        prob.add_O_point('O')
        assert prob.get_orig_point() == 'O'

    def test_save_load_roundtrip(self, prob):
        """序列化往返(逻辑层): pickle 验证继承类可序列化,加载后数据完整"""
        import pickle
        prob.add_symbol('t')
        prob.add_O_point('O')
        prob.add_point('A', '1', '0', '0', '', '')
        prob2 = pickle.loads(pickle.dumps(prob))
        assert prob2.point_names == prob.point_names
        assert prob2.orig_point == 'O'
        assert isinstance(prob2, type(prob))
        # 加载后仍可求解(逻辑可用)
        assert 'OA' in prob2.solve('OA')[0]

    def test_del_objs(self, prob):
        """del_objs: 删除对象"""
        prob.add_point('A', '1', '0', '0', '', '')
        prob.del_objs(['A'])
        assert 'A' not in prob.point_names

# ═══════════════════════════════════════════════════════
# 5. geo_solve.py: 求解 / 探索
# ═══════════════════════════════════════════════════════
@pytest.mark.xfail(reason="REFACTOR_PLAN: 模块未拆(暂缓),实现后转正")
class TestSolveContract:
    def test_solve_scalar(self, prob):
        """solve: 标量"""
        prob.add_point('A', '1', '2', '3', '', '')
        prob.add_point('B', '4', '6', '8', '', '')
        assert prob.solve('AB') == ['AB = \\left( ... \\right)'] or any('sqrt' in s for s in prob.solve('AB'))

    def test_solve_vec(self, prob):
        """solve_vec: 向量"""
        prob.add_point('A', '1', '2', '3', '', '')
        prob.add_point('B', '4', '6', '8', '', '')
        r = prob.solve_vec('vecAB')
        assert any('\\left( 3' in s for s in r)

    def test_solve_mult(self, prob):
        """solve_mult: 多表达式"""
        prob.add_symbol('t')
        prob.add_symbol('u')
        r = prob.solve_mult('t, u')
        assert len(r) >= 1

    def test_expore_extrema(self, prob):
        """expore_extrema: 极值"""
        prob.add_symbol('t')
        r = prob.expore_extrema('t**2 - 2*t + 1', 't', custom=True)
        assert any('\\left' in s for s in r)

    def test_expore_func(self, prob):
        """expore_func: 函数值"""
        prob.add_symbol('t')
        r = prob.expore_func('t**2', {'t': 2}, custom=True)
        assert '4' in r

    def test_expr_to_list_is_vector_guard(self, prob):
        """solve 对向量输入友好提示"""
        prob.add_point('A', '1', '0', '0', '', '')
        prob.add_point('B', '0', '1', '0', '', '')
        assert '向量' in prob.solve('vecAB')[0]
