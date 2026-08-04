"""3D几何计算器 - 未知数（符号）

与 2D 原版几乎相同 —— 未知数就是数学里的字母，和维度无关。
x, y, z 三个坐标轴符号由 SymPy 定义，用户自定义的符号（如 a, b, α）也走这里。

注意区分两个 Symbol：
  - GCSymbol 是"几何计算器符号"（用户创建的数学对象，可删可查依赖）
  - self.sp_symbol 是"SymPy 符号"（喂给 solve() 的引擎符号）
  两者用 id 关联：GCSymbol.id == 符号名，sp_symbol.name == 符号名

TODO(你可以手写): 3D 版如果需要"点坐标未知数"（x_A, y_A, z_A），
逻辑和 2D 完全一致，只是多了 z_A 一种。你可以在 Problem 里加。
"""

from typing import Optional
from functools import cache

from sympy import Symbol, latex

from .math_obj import MathObj
from type_hints import DomainSettings


def get_domain_latex_and_assumptions(domain_settings: Optional[DomainSettings] = None) -> tuple[str, dict[str, bool]]:
    """
    把前端的取值范围勾选翻译成：
    1. LaTeX 展示文本（如 \\mathbb{R}）
    2. SymPy 的假设（如 positive=True，帮助 solve 排除不符合范围的解）
    """
    def _bool(l=1, m=1, r=1):
        return [bool(i) for i in (l, m, r)]   # 注意推导式 in 后面要加括号成元组!

    if domain_settings is not None:
        domain_list = [domain_settings[i] for i in ['negative', 'zero', 'positive']]
    else:
        domain_list = _bool()

    # match 的 case 后面不能放函数调用(_bool() 会被当类模式),
    # 直接比较字面量列表即可
    match domain_list:
        case [True, True, True]:
            return r'\mathbb{R}', {'real': True}
        case [True, False, False]:
            return r'(-\infty, 0)', {'negative': True}
        case [True, True, False]:
            return r'(-\infty, 0]', {'nonpositive': True}
        case [False, False, True]:
            return r'(0, +\infty)', {'positive': True}
        case [False, True, True]:
            return r'[0, +\infty)', {'nonnegative': True}
        case [True, False, True]:
            return r'(-\infty, 0) \cup (0, +\infty)', {'nonzero': True}
    return '', {}


class GCSymbol(MathObj):
    def __init__(self, name: str, domain_settings: Optional[DomainSettings] = None):
        """
        几何计算器中的符号
        :param name: 符号名称（小写字母或希腊字母英文拼写，特殊时形如 x_A）
        :param domain_settings: 取值范围设置，None 视为全体实数
        """
        super().__init__(name)
        self.domain_latex, assumptions = get_domain_latex_and_assumptions(domain_settings)
        # 用 assumptions 创建 SymPy 符号
        self.sp_symbol = Symbol(name, **assumptions)

    @cache
    def get_name_latex(self) -> str:
        """符号自身的 LaTeX（如 a → 'a'）"""
        return latex(self.sp_symbol)

    @cache
    def get_domain_latex(self) -> str:
        """取值范围的 LaTeX（如 \\mathbb{R}）"""
        return self.domain_latex
