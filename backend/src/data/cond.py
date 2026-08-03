"""3D几何计算器 - 条件

一个条件 = 用户原始输入(LaTeX) + 解析出的方程列表(eqs)。
比如用户添加"AB ⊥ CD"，raw_latex 是 AB ⊥ CD 的 LaTeX 形式，
eqs 是把它翻译成的代数方程 [a1*a2 + b1*b2 == 0, ...]。

to_raw_latex 是字符串美化器：把用户输入表达式变成漂亮的 LaTeX。
它和 problem.py 的 _eval_str_expr 是"表兄弟"：
  - _eval_str_expr: 人话 → SymPy 代码（机器可执行）
  - to_raw_latex:   人话 → LaTeX（人可读）
  两者各自维护一套正则规则，互相独立（2D 原版就是这样设计的）。

TODO(你来补全)：
  1. map_vec_coord / to_raw_latex 抄 2D 原版（注意 3D 向量是三元组）
  2. 3D 新增的 DSL 记号在这里加美化规则，例如：
     - VABCD → V_{ABCD}（四面体体积）
     - nABC → \\vec{n}_{ABC}（平面法向量）
     - 点面距、线面角等（按你的 DSL 设计）
  3. Cond 类本身和 2D 一样，不用改（raw_latex 做 id，eqs 存方程）
"""

import re

from sympy import Eq, latex, sympify
from sympy.printing.latex import LatexPrinter

from .math_obj import MathObj
from vec_parse_utils import mark_vec_coord


def map_vec_coord(expr: str) -> tuple[str, dict[str, str]]:
    """
    将向量的坐标表示映射到一个临时变量上，让 sympify 能把它当普通符号解析。
    （SymPy 的 sympify(evaluate=False) 也阻止不了向量"数乘"执行，所以先替换成别名）
    :param expr: 原始字符串表达式
    :return: (替换后的表达式, 别名→LaTeX 映射表)
    """
    # TODO(你来补全): 抄 2D 原版实现（逻辑与维度无关，Matrix([x,y]) 变 Matrix([x,y,z]) 即可）
    raise NotImplementedError('TODO: 实现 map_vec_coord')


def to_raw_latex(expr: str) -> str:
    """
    生成用户原始输入的表达式的 LaTeX
    只能是单个表达式
    """
    # TODO(你来补全): 抄 2D 原版，并补充 3D 新记号的美化规则。
    # 2D 已有的规则示例：
    #   vecAB → \\overrightarrow{AB}
    #   ABC → \\triangle ABC
    #   angABC → \\angle ABC
    #   xA → x_A
    #   dAtBC → d_{A 到 BC}
    raise NotImplementedError('TODO: 实现 to_raw_latex')


class Cond(MathObj):
    def __init__(self, raw_latex: str, eqs: list):
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
