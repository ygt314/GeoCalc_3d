"""GCPoint 3D点 —— 完整测试面

✅ 已实现,全部测试通过(2026-08-03 实现)

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

    def test_init_basic(self):
        """点名字 + 坐标"""
        p = GCPoint('A', 1, 2, 3)
        assert p.id == 'A'
        assert p.x == 1
        assert p.y == 2
        assert p.z == 3

    def test_sp_point_is_point3d(self):
        """sp_point 必须是 SymPy Point3D"""
        from sympy import Point3D
        p = GCPoint('A', 1, 2, 3)
        assert isinstance(p.sp_point, Point3D)
        assert p.sp_point.coordinates == (1, 2, 3)

    def test_symbolic_coord(self):
        """坐标可以是符号表达式(点由未知数确定)"""
        from sympy import Symbol
        t = Symbol('t', real=True)
        p = GCPoint('A', t, 2 * t, 3)
        assert p.x == t


class TestPointDisplay:
    """点的 LaTeX 展示契约"""

    def test_get_latex(self):
        """格式:A left( x, y, z right)"""
        p = GCPoint('A', 1, 2, 3)
        latex_str = p.get_latex()
        assert 'A' in latex_str
        assert '1' in latex_str
        assert '2' in latex_str
        assert '3' in latex_str
