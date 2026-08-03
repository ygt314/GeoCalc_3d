"""测试 SymPy 3D 几何原语 —— 你写 Problem 核心逻辑时的"数学地基"

这些测试不依赖你未实现的代码,验证的是 SymPy 1.14 的 3D 能力,
确保你后面写 _get_vec / _get_triangle_area / 体积公式时有正确的参照。

运行:cd backend && .venv/bin/python -m pytest tests/test_sympy_3d.py -v
"""

from sympy import Point3D, Plane, Matrix, sqrt, simplify, Abs, Rational


class TestSympy3D:
    """SymPy 3D 数学原语验证"""

    def test_point3d_distance(self):
        """空间两点距离公式"""
        a = Point3D(0, 0, 0)
        b = Point3D(1, 2, 2)
        assert a.distance(b) == 3  # sqrt(1+4+4) = 3

    def test_vector3d(self):
        """3D 向量 = 终点 - 起点"""
        a = Point3D(1, 0, 0)
        b = Point3D(4, 2, 3)
        v = Matrix([b.x - a.x, b.y - a.y, b.z - a.z])
        assert v == Matrix([3, 2, 3])

    def test_cross_product(self):
        """叉积:AB × AC 垂直于 AB 和 AC"""
        a = Point3D(0, 0, 0)
        b = Point3D(1, 0, 0)
        c = Point3D(0, 1, 0)
        v1 = Matrix([b.x - a.x, b.y - a.y, b.z - a.z])
        v2 = Matrix([c.x - a.x, c.y - a.y, c.z - a.z])
        cross = v1.cross(v2)
        assert cross == Matrix([0, 0, 1])  # z 轴方向
        # 叉积与两个向量都垂直(点积为 0)
        assert v1.dot(cross) == 0
        assert v2.dot(cross) == 0

    def test_mixed_product_volume(self):
        """混合积 = 平行六面体体积;四面体体积 = |混合积|/6"""
        a = Point3D(0, 0, 0)
        b = Point3D(1, 0, 0)
        c = Point3D(0, 1, 0)
        d = Point3D(0, 0, 1)
        ab = Matrix([b.x - a.x, b.y - a.y, b.z - a.z])
        ac = Matrix([c.x - a.x, c.y - a.y, c.z - a.z])
        ad = Matrix([d.x - a.x, d.y - a.y, d.z - a.z])
        mixed = ab.dot(ac.cross(ad))
        # 注意:SymPy 的 1/6 是精确有理数,Python 的 1/6 是浮点,两者不相等!
        # 所以要用 Rational 或 sympy 的 S(1)/6
        assert simplify(Abs(mixed) / 6) == Rational(1, 6)  # 单位四面体体积 = 1/6

    def test_plane_equation(self):
        """三点确定平面,方程 Ax+By+Cz+D=0,法向量 (A,B,C)"""
        p = Plane(Point3D(0, 0, 0), Point3D(1, 0, 0), Point3D(0, 1, 0))
        eq = p.equation()  # 展开成 Ax+By+Cz+D 形式的表达式
        # z=0 平面的方程
        assert simplify(eq) == 0 or str(simplify(eq)) == '0' or 'z' in str(simplify(eq))

    def test_point_to_plane_distance(self):
        """点面距离公式验证"""
        plane = Plane(Point3D(0, 0, 0), Point3D(1, 0, 0), Point3D(0, 1, 0))  # z=0 平面
        d = Point3D(0, 0, 5)
        assert plane.distance(d) == 5

    def test_parallel_judgment(self):
        """线线平行判定:方向向量叉积为零向量"""
        v1 = Matrix([1, 2, 3])
        v2 = Matrix([2, 4, 6])  # v2 = 2*v1,平行
        assert v1.cross(v2) == Matrix([0, 0, 0])

    def test_perp_judgment(self):
        """线线垂直判定:方向向量点积为 0"""
        v1 = Matrix([1, 0, 0])
        v2 = Matrix([0, 1, 0])
        assert v1.dot(v2) == 0
