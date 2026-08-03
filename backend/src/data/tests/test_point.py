"""GCPoint 3D点 —— 完整测试面

⚠️ 注意:GCPoint 是 TODO(待你实现)。这里写好契约测试,xfail 标记。
【你实现后:删除 @pytest.mark.xfail 装饰器,测试就会转绿】

覆盖:
  - 初始化(名字 + 三维坐标)
  - sp_point 是 SymPy Point3D(可算距离)
  - get_latex 三元组展示
"""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from data.point import GCPoint  # noqa: E402


class TestPointInit:
    """GCPoint 初始化契约"""

    @pytest.mark.xfail(reason='TODO: 待实现 GCPoint.__init__', strict=False)
    def test_init_basic(self):
        """点名字 + 坐标"""
        p = GCPoint('A', 1, 2, 3)
        assert p.id == 'A'
        assert p.x == 1
        assert p.y == 2
        assert p.z == 3

    @pytest.mark.xfail(reason='TODO: 待实现 GCPoint.__init__', strict=False)
    def test_sp_point_is_point3d(self):
        """sp_point 必须是 SymPy Point3D"""
        from sympy import Point3D
        p = GCPoint('A', 1, 2, 3)
        assert isinstance(p.sp_point, Point3D)
        assert p.sp_point.coordinates == (1, 2, 3)

    @pytest.mark.xfail(reason='TODO: 待实现 GCPoint.__init__', strict=False)
    def test_symbolic_coord(self):
        """坐标可以是符号表达式(点由未知数确定)"""
        from sympy import Symbol
        t = Symbol('t', real=True)
        p = GCPoint('A', t, 2 * t, 3)
        assert p.x == t


class TestPointDisplay:
    """点的 LaTeX 展示契约"""

    @pytest.mark.xfail(reason='TODO: 待实现 GCPoint(依赖 __init__)', strict=False)
    def test_get_latex(self):
        """格式:A left( x, y, z right)"""
        p = GCPoint('A', 1, 2, 3)
        latex_str = p.get_latex()
        assert 'A' in latex_str
        assert '1' in latex_str
        assert '2' in latex_str
        assert '3' in latex_str
