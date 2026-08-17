"""3D几何计算器 - 条件

一个条件 = 用户原始输入(LaTeX) + 解析出的方程列表(eqs)。
比如用户添加"AB ⊥ CD"，raw_latex 是 AB ⊥ CD 的 LaTeX 形式，
eqs 是把它翻译成的代数方程 [a1*a2 + b1*b2 == 0, ...]。

to_raw_latex 是字符串美化器：把用户输入表达式变成漂亮的 LaTeX。
它和 problem.py 的 _eval_str_expr 是"表兄弟"：
  - _eval_str_expr: 人话 → SymPy 代码（机器可执行）
  - to_raw_latex:   人话 → LaTeX（人可读）
  两者各自维护一套正则规则，互相独立（2D 原版就是这样设计的）。
"""

import re

from sympy import Eq, latex, sympify

from .math_obj import MathObj
from vec_parse_utils import mark_vec_coord


def map_vec_coord(expr: str) -> tuple[str, dict[str, str]]:
    """
    将向量的坐标表示映射到一个临时变量上，让 sympify 能把它当普通符号解析。
    （SymPy 的 sympify(evaluate=False) 也阻止不了向量"数乘"执行，所以先替换成别名）
    :param expr: 原始字符串表达式
    :return: (替换后的表达式, 别名→LaTeX 映射表)
    """
    mapping = {}
    while True:
        left_index = expr.find('Matrix([')
        if left_index != -1:
            right_index = expr.find('])') + 2
            vec_coord = expr[left_index:right_index]
            alias = f'vec{hash(vec_coord) ** 2}coord'
            expr = expr.replace(vec_coord, alias)
            mapping[alias] = latex(sympify(vec_coord, evaluate=False), mul_symbol='dot')
        else:
            return expr, mapping


def to_raw_latex(expr: str) -> str:
    """
    生成用户原始输入的表达式的 LaTeX
    只能是单个表达式
    2D 已有的规则：
    vecAB → \\overrightarrow{AB}
    ABC → \\triangle ABC
    angABC → \\angle ABC
    xA/yA → x_A/y_A zA也支持
    k|b规则已丢弃，因为立体几何无法定义斜率截距
    StABC -> S△ABC 改为叉积计算|AB \\cross BC|/2
    dAtBC → d_{A 到 BC} = |AB \\cross BC|/|BC|
    3D 新规则：
    nABC 法向量 n_{ABC} = AB \\cross BC
    angvABCD 向量夹角 <AB,CD> [0, pi)
    angrABCD 二面角 ∠A-BC-D [0, pi)
    angcAB_CD 所成角 AB与CD [0, pi/2]
    dAtpBCD → d_{A 到 平面BCD} = |n \\dot AB|/|n|
    vABCD 四面体体积 V_{A-BCD} = |AB \\dot (BC \\cross CD)|/6
    vABC-OPQ -> 三棱台（柱）体积
    """
    expr = (mark_vec_coord(expr)
                .replace('deg', '* gcdeg') # SymPy 内有个函数就叫 ``deg``，故在此做区分
                .replace(' cross ', 'xxx') # 叉乘顺序不变
                .replace('_','x') # sympify 后 _ 会变成 _{}
                .replace('dot', '*'))

    expr, mapping = map_vec_coord(expr)

    expr = latex(sympify(expr, evaluate=False), mul_symbol='dot')
    print("[debug]:sympify_latex:")
    print(expr)
    for alias, vec_coord_latex in mapping.items():
        expr = expr.replace(alias, vec_coord_latex)

    rules = [
        # ·gcdeg -> °
        (r'\\cdot\s+gcdeg', r'^{\\circ}'),
        # 叉乘
        (r'xxx', r' \\times '),
        # vecAB -> \overrightarrow{AB}
        (r'\bvec([A-Z]{2})\b', r'\\overrightarrow{\1}'),
        # angcAB_CD -> 所成角
        (r'\bangc([A-Z]{2})x([A-Z]{2})\b', r'\1 与 \2 所成角'),
        (r'\bangc([A-Z]{3})x([A-Z]{2})\b', r'平面\1 与 \2 所成角'),
        (r'\bangc([A-Z]{2})x([A-Z]{3})\b', r'\1 与 平面\2 所成角'),
        (r'\bangc([A-Z]{3})x([A-Z]{3})\b', r'平面\1 与 平面\2 所成角'),
        # ABC -> △ABC
        (r'\b([A-Z]{3})\b', r'\\triangle \1'),
        # pABC -> 平面ABC
        (r'\bp([A-Z]{3})\b', r'平面\1'),
        # ABCD -> 平面ABCD
        (r'\b([A-Z]{4})\b', r'平面\1'),
        # angABC -> ∠ABC
        (r'\bang([A-Z]{3})\b', r'\\angle \1'),
        # 删除多余点号
        (r'(?<=[0-9a-z])\s*\\cdot\s*(?=[a-zA-Z]|\\overrightarrow)', r' '),
        # StABC -> S△ABC
        (r'\bSt([A-Z]{3})\b', r'S_{\\triangle \1}'),
        # xA -> x_A
        (r'\b(x|y|z)([A-Z])\b', r'\1_\2'),
        # dAtBC -> d_{A 到 BC}
        (r'\bd([A-Z])t([A-Z]{2})\b', r'd_{\1 到 \2}'),
        # nABC -> 平面法向量
        (r'\bn([A-Z]{3})\b', r'\\overrightarrow{n}_{平面\1}'),
        # angvABCD -> 向量夹角 <AB, CD>
        (r'\bangv([A-Z]{2})([A-Z]{2})\b', r'<\\overrightarrow{\1}, \\overrightarrow{\2}>'),
        # angrABCD -> 二面角 ∠A-BC-D
        (r'\bangr([A-Z])([A-Z]{2})([A-Z])\b', r'\\angle \1-\2-\3'),
        # dAtpBCD -> 点到平面距离
        (r'\bd([A-Z])tp([A-Z]{3})\b', r'd_{\1 到 平面\2}'),
        # vABCD -> 四面体体积
        (r'\bv([A-Z])([A-Z]{3})\b', r'V_{四面体\1-\2}'),
        # vABC_OPQ -> 三棱台（柱）体积
        (r'\bv([A-Z]{3})x([A-Z]{3})\b', r'V_{三棱柱\1-\2}')
    ]
    for pattern, repl in rules:
        expr = re.sub(pattern, repl, expr)

    print("[debug]:latex_subed:")
    print(expr)
    return expr


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
