"""3D几何计算器 - 条件

一个条件 = 用户原始输入(LaTeX) + 解析出的方程列表(eqs)。
比如用户添加"AB ⊥ CD"，raw_latex 是 AB ⊥ CD 的 LaTeX 形式，
eqs 是把它翻译成的代数方程 [a1*a2 + b1*b2 == 0, ...]。
"""

from sympy import Eq, latex

from .math_obj import MathObj


class Cond(MathObj):
    def __init__(self, raw_latex: str, eqs: list[Eq]):
        """
        一个条件
        :param raw_latex: 用户原始输入的 LaTeX 形式（同时用作本对象的 id）
        :param eqs: 解析得到的方程列表（可能多个，比如正方形要 3 个方程）
        """
        super().__init__(raw_latex)
        self.eqs = eqs

    def get_raw_latex(self) -> str:
        """原始条件的 LaTeX（前面用原始 LaTeX 做了 id，直接返回即可）"""
        return self.id

    def get_eqs_latex(self) -> str:
        """把方程列表渲染成 LaTeX 串（多个方程用空格隔开，每个带 $$ $$）"""
        return ' '.join(f'$$ {latex(eq)} $$' for eq in self.eqs)
