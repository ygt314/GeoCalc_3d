"""3D几何计算器 - 点

与 2D 原版的核心区别：坐标从 (x, y) 变成 (x, y, z)。
点可以是"具体点"（坐标是数字表达式）也可以是"待定点"（坐标含未知数，
比如 x_A, y_A, z_A —— 这些未知数由 Problem.add_point 自动创建）。

SymPy 3D 对应类型：Point3D（在 sympy.geometry.point3d 里，需要导入）。
"""

from functools import cache
# Expr用来类型注释
from sympy import Expr

from sympy import Point3D,latex

from .math_obj import MathObj

class GCPoint(MathObj):
    def __init__(self, name: str, x: Expr, y: Expr, z: Expr):
        """
        几何计算器中的点
        :param name: 点名称（一个大写字母）
        :param x: 横坐标（数字表达式或含未知数的表达式）
        :param y: 纵坐标
        :param z: 竖坐标  ← 3D 新增
        """
        super().__init__(name)
        # 存坐标并创建 Point3D
        self.x = x
        self.y = y
        self.z = z
        self.sp_point = Point3D(x, y, z)

    @cache
    def get_latex(self) -> str:
        """点的 LaTeX 展示：A \\left( x, y, z \\right)"""
        # 参照 2D 原版，输出三元坐标
        return fr'{self.id} \left( {latex(self.x)}, {latex(self.y)}, {latex(self.z)} \right)'
