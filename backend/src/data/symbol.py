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

    TODO(你来补全): 抄 2D 原版的实现即可，这部分与维度无关，一字不改。
    对应关系（前端勾了哪些 → latex / assumptions）：
      [负, 零, 正] = [T,T,T] → \\mathbb{R}              → {'real': True}
      [T,F,F]       → (-\\infty, 0)                      → {'negative': True}
      [T,T,F]       → (-\\infty, 0]                      → {'nonpositive': True}
      [F,F,T]       → (0, +\\infty)                      → {'positive': True}
      [F,T,T]       → [0, +\\infty)                      → {'nonnegative': True}
      [T,F,T]       → (-\\infty,0) ∪ (0,+\\infty)        → {'nonzero': True}
    """
    raise NotImplementedError('TODO: 抄 2D 原版 data/symbol.py 的 get_domain_latex_and_assumptions')


class GCSymbol(MathObj):
    def __init__(self, name: str, domain_settings: Optional[DomainSettings] = None):
        """
        几何计算器中的符号
        :param name: 符号名称（小写字母或希腊字母英文拼写，特殊时形如 x_A）
        :param domain_settings: 取值范围设置，None 视为全体实数
        """
        super().__init__(name)
        self.domain_latex, assumptions = get_domain_latex_and_assumptions(domain_settings)
        # TODO(你来补全): 用 assumptions 创建 SymPy 符号
        #   self.sp_symbol = Symbol(name, **assumptions)
        raise NotImplementedError('TODO: 创建 self.sp_symbol')

    @cache
    def get_name_latex(self) -> str:
        """符号自身的 LaTeX（如 a → 'a'）"""
        return latex(self.sp_symbol)

    @cache
    def get_domain_latex(self) -> str:
        """取值范围的 LaTeX（如 \\mathbb{R}）"""
        return self.domain_latex
