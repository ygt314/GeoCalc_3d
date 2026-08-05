"""data 包初始化

注意:这里调用 override_latex() 全局覆盖 sympy.latex,
让所有向量输出圆括号坐标形式 left( x, y, z right)。
(2D 原版是在 problem.py 顶部调用的;这里更早,data 层一导入就生效)
"""

from custom_latex import override_latex

override_latex()

from .math_obj import MathObj
from .symbol import GCSymbol
from .point import GCPoint
from .cond import Cond, to_raw_latex
