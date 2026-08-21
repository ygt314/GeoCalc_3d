"""
DSL 语法区 - 表达式翻译官
to_raw_latex 是字符串美化器：把用户输入表达式变成漂亮的 LaTeX。
它和 to_raw_expr 是"表兄弟"：
  - to_raw_expr: 人话 → SymPy 代码（机器可执行）
  - to_raw_latex:   人话 → LaTeX（人可读）
两者各自维护一套正则规则，互相独立（2D 原版就是这样设计的）。
"""

import re

from sympy import latex, sympify, Symbol

from vec_parse_utils import mark_vec_coord

# 新增z轴符号
x = Symbol('x', real=True)
y = Symbol('y', real=True)
z = Symbol('z', real=True)

# 希腊字母的英文拼写（除 pi 外）
VALID_GREEK_SPELLINGS = [
    'alpha', 'beta', 'gamma', 'delta', 'epsilon', 'zeta', 'eta', 'theta',
    'iota', 'kappa', 'lambda', 'mu', 'nu', 'xi', 'omicron',
    'rho', 'sigma', 'tau', 'upsilon', 'phi', 'chi', 'psi', 'omega'
]

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
        (r'\bv([A-Z]{3})x([A-Z]{3})\b', r'V_{\1-\2}')
    ]
    for pattern, repl in rules:
        expr = re.sub(pattern, repl, expr)

    print("[debug]:latex_subed:")
    print(expr)
    return expr


def to_raw_expr(expr: str) -> str:
    """
    一串正则替换把"人话"变成 Python 代码
    2D 版的规则表（你在 3D 版要扩展它）：
    '^' → '**'                              幂运算
    'deg' → '* pi / 180'                    角度制转弧度
    数字 → Integer(n)                       防止 1/2 变小数
    'dot' → '@ dot @'                       向量点乘（中缀）
    a-z/希腊字母 → self._get_sp_symbol()    未知数
    xA/yA → self._get_x_of/y_of('A')        点坐标，现也支持z
    AB → self._get_distance('AB')           线段长度
    angABC → self._get_angle('ABC')         角度
    vecAB → self._get_vec('AB')             向量
    StABC → self._get_triangle_area('ABC')  三角形面积
    kAB/bAB → 斜率/截距（3D 删除！改方向向量）
    
    3D 新增规则（你来设计 DSL）：
    nABC 法向量 n_{ABC} = AB \\cross BC
    angvABCD 向量夹角 <AB,CD>
    angrABCD 二面角 ∠A-BC-D
    angcAB_CD 所成角 AB与CD
    dAtpBCD → d_{A 到 平面BCD} = |n \\dot AB|/|n|
    vABCD 四面体体积 V_{A-BCD} = |AB \\dot (BC \\cross CD)|/6
    vABC_OPQ -> 三棱台(柱）体积
    """
    expr = mark_vec_coord(expr)
    rules = [
        # 幂运算符
        (r'\^', '**'),
        # 角度制
        ('deg', '* pi / 180'),
        # 给整数套上 ``Integer()``，防止一除变成小数
        (r'(?<!\.)\b(\d+)\b(?!\.)', r'Integer(\1)'),
        # 向量点乘
        ('dot', '@ dot @'),
        # 向量叉乘
        ('cross', '@ cross @'),
        # 未知数（不考虑排除 x, y 了，反正最后会报错）
        (r'\b([a-z]|' + '|'.join(VALID_GREEK_SPELLINGS) + r')\b', r"self._get_sp_symbol('\1')"),
        # 访问点坐标
        (r'\b(x|y|z)([A-Z])\b', r"self._get_\1_of('\2')"),
        # 线段长度
        (r'\b([A-Z]{2})\b', r"self._get_distance('\1')"),
        # 角度
        (r'\bang([A-Z]{3})\b', r"self._get_angle('\1')"),  # bang! 我这奇妙的笑点 233
        # 向量夹角 <AB, CD>
        (r'\bangv([A-Z]{4})\b', r"self._get_angv('\1')"),
        # 二面角 ∠A-BC-D
        (r'\bangr([A-Z])([A-Z]{2})([A-Z])\b', r"self._get_angr('\1','\2','\3')"),
        # 所成角
        (r'\bangc([A-Z]{2,3})_([A-Z]{2,3})\b', r"self._get_angc('\1','\2')"),
        # 两个大写字母的向量
        (r'\bvec([A-Z]{2})\b', r"self._get_vec('\1')"),
        # 平面法向量
        (r'\bn([A-Z]{3})\b', r"self._get_plane_normal('p\1')"),
        # 三角形面积
        (r'\bSt([A-Z]{3})\b', r"self._get_triangle_area('\1')"),
        # 四面体体积
        (r'\bv([A-Z]{4})\b', r"self._get_tetrahedron_volume('\1')"),
        # 三棱台（柱）体积
        (r'\bv([A-Z]{3})_([A-Z]{3})\b', r"self._get_Ss_volume('\1','\2')"),
        # 点到直线的距离
        (r'\bd([A-Z])t([A-Z]{2})\b', r"self._get_distance_from_point_to_line('\1','\2')"),
        # 点到平面距离
        (r'\bd([A-Z])tp([A-Z]{3})\b', r"self._get_distance_point_to_plane('\1','\2')")
    ]
    for pattern, repl in rules:
        expr = re.sub(pattern, repl, expr)

    return expr
