"""3D几何计算器 - 核心：Problem 类

这是整个项目的"大脑"。2D 原版 478 行，本文件是骨架 + 详细注释，
核心实现（TODO 标注处）由你对照 2D 原版手写补全 —— 这正是学习的目的。

## Problem 的职责（记住这张地图）

  1. 管理所有数学对象：self.math_objs（id → 对象）
  2. 维护依赖图：requirements_tracker + track_requirement（装饰器）
  3. 把用户字符串表达式编译成 SymPy 代码：_eval_str_expr
  4. 把几何条件翻译成代数方程：add_* 系列方法（@AddCond 装饰器）
  5. 求解：solve() —— 把所有方程丢给 SymPy 的 solve

## 2D → 3D 核心变化清单（你在 TODO 处要做的）

  - 点的坐标从 (x, y) → (x, y, z)，所有 _get_* 方法加 z 分量
  - _get_line（Line2D）→ 线在 3D 里不能再用"一般式 ax+by+c=0"表示！
    3D 直线用：方向向量 + 参数方程，或用 SymPy 的 Line3D
  - 斜率 k / 截距 b 概念在 3D 消失（3D 线没有单一斜率）→ 改用方向向量
  - 新增 _get_plane（平面）、法向量、点面距离、体积等
  - 条件类型扩展：线面平行/垂直、面面平行/垂直、共面、异面、四面体体积…
"""

from custom_latex import override_latex

override_latex()

from typing import Never, Optional, Callable
import re
import functools
from abc import ABC, abstractmethod
from collections import deque
import pickle
# 新增Plane，并为点线适配3D；删除Segment无用项，距离就是模长
# 暂时新增asin适配线面所成角
from sympy import Symbol, Expr, symbols, simplify, Eq, Line3D, solve, Point3D, Plane, Matrix, asin, acos, latex, Abs, sqrtdenest
from sympy import diff, sqrt, sin, cos, tan, pi, Integer  # noqa
from sympy.logic.boolalg import BooleanTrue, BooleanFalse
from webview import windows, FileDialog
# 新增叉积cross
from data import MathObj, GCSymbol, GCPoint, Cond, to_raw_latex
from type_hints import DomainSettings, LatexItem
from vec_parse_utils import mark_vec_coord, dot, cross

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


def track_requirement(func):
    """在执行访问数学对象的函数时，追踪记录它访问了谁
    （抄 2D 原版，一字不改 —— 依赖追踪与维度无关）
    """
    @functools.wraps(func)
    def wrapper(self: 'Problem', name: str):
        self.requirements_tracker.add(self.math_objs[name])
        return func(self, name)
    return wrapper


class AddCond(ABC):
    """条件添加装饰器（抄 2D 原版，一字不改）
    职责：把用户输入拼成 LaTeX id → 调用被装饰方法得到方程列表 → 化简 → 过滤恒真/恒假 → 添加
    """
    def __init__(self, op: str):
        self.op = op

    @abstractmethod
    def get_raw_latex(self, *args) -> str:
        """给出原始形式的 LaTeX"""
        ...

    def __call__(self, func: Callable[['Problem', str, str], list[Eq]]):
        def wrapper(problem: 'Problem', *args) -> None | Never:
            raw_latex = self.get_raw_latex(*args)
            # 化简方程（组）并过滤 True
            eqs = []
            for eq in func(problem, *args):
                eq = simplify(eq)
                if isinstance(eq, BooleanFalse):
                    raise ValueError('该条件不可能成立！')
                if not isinstance(eq, BooleanTrue):
                    eqs.append(eq)
            if len(eqs) == 0:
                raise ValueError('该条件一定成立，不需要添加')
            problem.add_cond(Cond(raw_latex, eqs))

        return wrapper


class AddBinCond(AddCond):
    """二元条件：input1 OP input2（如 AB = CD、AB ⊥ CD）
    抄 2D 原版即可：f'{to_raw_latex(input1)} {self.op} {to_raw_latex(input2)}'
    """
    def get_raw_latex(self, input1: str, input2: str) -> str:
        return f'{to_raw_latex(input1)} {self.op} {to_raw_latex(input2)}'


class AddUnaryCond(AddCond):
    """一元条件：OP input1（如"平行四边形 ABCD"、"等边三角形 ABC"）
    抄 2D 原版即可：f'{self.op} {input1}'
    """
    def get_raw_latex(self, input1: str) -> str:
        return f'{self.op} {input1}'


class Problem:
    def __init__(self):
        self.math_objs: dict[str, MathObj] = {}
        self.symbol_names: list[str] = []
        self.point_names: list[str] = []
        self.cond_ids: list[str] = []

        # 用于临时存放正在添加的新对象依赖哪些对象
        self.requirements_tracker: set[MathObj] = set()

    # ═══════════════════════════════════════════════════════
    # 第一部分：对象管理（抄 2D 原版，基本不改）
    # ═══════════════════════════════════════════════════════

    def _add_math_obj(self, obj: MathObj) -> None:
        """添加数学对象，并把 tracker 里的依赖关系固化到对象上"""
        self.math_objs[obj.id] = obj
        # 添加依赖关系并清空追踪器
        for requirement in self.requirements_tracker:
            requirement.add_required_by(obj)
        self.requirements_tracker.clear()

    def add_cond(self, cond: Cond) -> None:
        """添加条件并把 id 加到列表里"""
        self._add_math_obj(cond)
        self.cond_ids.append(cond.id)

    # ═══════════════════════════════════════════════════════
    # 第二部分：数学对象访问器（_get_* 系列）★ 3D 改动核心区
    # 每个方法上都挂了 @track_requirement，访问即记录依赖
    # ═══════════════════════════════════════════════════════

    @track_requirement
    def _get_sp_symbol(self, name: str) -> Symbol:
        """获取 SymPy 符号（3D 版不改）"""
        return self.math_objs[name].sp_symbol  # type: ignore

    @track_requirement
    def _get_x_of(self, name: str):
        """获取点的 x 坐标（3D 版不改，再加一个 _get_z_of）"""
        return self.math_objs[name].x  # type: ignore

    @track_requirement
    def _get_y_of(self, name: str):
        """获取点的 y 坐标（3D 版不改）"""
        return self.math_objs[name].y  # type: ignore

    # 新增 _get_z_of（3D 特有）
    @track_requirement
    def _get_z_of(self, name: str):
        return self.math_objs[name].z

    @track_requirement
    def _get_sp_point(self, name: str) -> Point3D:
        """获取 SymPy 点对象（3D 版返回 Point3D）"""
        return self.math_objs[name].sp_point  # type: ignore

    def _get_line(self, name: str) -> Line3D:
        """两点确定一条直线"""
        p1 = self._get_sp_point(name[0])
        p2 = self._get_sp_point(name[1])
        return Line3D(p1, p2)

    def _get_plane(self, name: str) -> Plane:
        """新增：由三个点确定平面"""
        p1 = self._get_sp_point(name[0])
        p2 = self._get_sp_point(name[1])
        p3 = self._get_sp_point(name[2])
        return Plane(p1, p2, p3)

    def _get_vec(self, name: str) -> Matrix:
        """获取向量（2D: Matrix([x2-x1, y2-y1])；3D: 方向向量转矩阵"""
        return Matrix(self._get_line(name).direction)

    def _get_distance(self, name: str) -> Expr:
        """获取两点距离，其实是向量模长"""
        return self._get_vec(name).norm()

    def _get_angle(self, name: str) -> Expr:
        """获取三点夹角 ∠ABC（3D 中三个点总是共面，公式与 2D 相同：向量夹角）"""
        v1 = self._get_vec(name[1::-1])
        v2 = self._get_vec(name[1:])
        # [improve flag]其实直接用余弦值好一点，这对sympy友好一点，但是不好适配
        return acos(v1.dot(v2) / (v1.norm() * v2.norm()))

    def _get_triangle_area(self, name: str) -> Expr:
        """获取三角形面积（3D：不在坐标平面上的三角形，要用叉积模长/2）"""
        v1 = self._get_vec(name[1::-1])
        v2 = self._get_vec(name[1:])
        # 面积 = |AB × AC| / 2（叉积模长的一半）
        return v1.cross(v2).norm()/2

    # 新增 3D 访问器
    # [improve_flag]暂时与2D一样使用（反）正余弦值
    def _get_plane_normal(self, name: str) -> Matrix:
        """平面法向量，sympy会自动化简"""
        return Matrix(self._get_plane(name[0:3]).normal_vector)
    
    def _get_angv(self, vv: str) -> Expr:
        """angvABCD 向量夹角 <AB,CD> [0, pi)"""
        v1 = self._get_vec(vv[0:2])
        v2 = self._get_vec(vv[2:])
        return acos(v1.dot(v2) / (v1.norm() * v2.norm()))

    def _get_angr(self, m: str,l: str,n: str) -> Expr:
        """angrABCD 二面角 ∠A-BC-D [0, pi)"""
        v1 = self._get_plane_normal(m+l)
        v2 = self._get_plane_normal(n+l)
        return acos(v1.dot(v2) / (v1.norm() * v2.norm()))

    def _get_angc(self,a: str,b: str) -> Expr:
        """angcAB_CD 所成角 AB与CD [0, pi/2]"""
        vn = lambda x:self._get_vec(x) if len(x)==2 else self._get_plane_normal(x[0:3])
        v1,v2 = vn(a),vn(b)
        vv = v1.norm() * v2.norm()
        if len(a) == len(b):
            return acos(Abs(v1.dot(v2)) / vv)
        else:
            return asin(Abs(v1.dot(v2)) / vv)

    def _get_distance_from_point_to_line(self, point: str, line: str) -> Expr:
        """
        点到直线的距离
        https://github.com/zhdbk3/GeometryCalculator/issues/6#issuecomment-3124395226
        这里直接调用sympy几何距离方法
        """
        p = self._get_sp_point(point)
        l = self._get_line(line)
        return p.distance(l)

    def _get_distance_point_to_plane(self, point: str, plane: str) -> Expr:
        """点面距离 |ax0 + by0 + cz0 + d| / sqrt(a²+b²+c²)"""
        p = self._get_sp_point(point)
        p1 = self._get_plane(plane[0:3])
        return p.distance(p1)

    def _get_tetrahedron_volume(self, name: str) -> Expr:
        """
        四面体体积 V = |AB · (AC × AD)| / 6（混合积）
        = 底面面积 × 点面距离 / 3
        """
        sbcd = self._get_triangle_area(name[1:])
        dh = self._get_distance_point_to_plane(name[0], name[1:])
        return sbcd * dh / 3
    def _get_Ss_volume(self, t: str, t1: str) -> Expr:
        """
        三棱台（柱）体积 V = (S+sqrt(S·s)+s) · H / 3
        特别的，三棱柱 V = S · H
        [improve_flag]暂时不考虑面平行的问题
        """
        s = self._get_triangle_area(t)
        s1 = self._get_triangle_area(t1)
        dh = self._get_distance_point_to_plane(t[0], t1)
        if s == s1: return s*dh
        return (s+sqrt(s*s1)+s1) * dh / 3
    # ═══════════════════════════════════════════════════════
    # 第三部分：字符串表达式 → SymPy 代码 ★ 整个项目最巧妙的部分
    # ═══════════════════════════════════════════════════════

    def _eval_str_expr(self, expr: str) -> Expr | Never:
        """
        尝试解析字符串表达式，解析失败会报错
        原理：一串正则替换把"人话"变成 Python 代码，然后 eval

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
        vABC-OPQ -> 三棱台(柱）体积
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
            (r'\bn([A-Z]{3})\b', r"self._get_plane_normal('\1')"),
            # 三角形面积
            (r'\bSt([A-Z]{3})\b', r"self._get_triangle_area('\1')"),
            # 四面体体积
            (r'\bv([A-Z]{4})\b', r"self._get_tetrahedron_volume('\1')"),
            # 三棱台（柱）体积
            (r'\bv([A-Z]{3})-([A-Z]{3})\b', r"self._get_Ss_volume('\1','\2')"),
            # 点到直线的距离
            (r'\bd([A-Z])t([A-Z]{2})\b', r"self._get_distance_from_point_to_line('\1','\2')"),
            # 点到平面距离
            (r'\bd([A-Z])tp([A-Z]{3})\b', r"self._get_distance_point_to_plane('\1','\2')")
        ]
        for pattern, repl in rules:
            expr = re.sub(pattern, repl, expr)
        return simplify(eval(expr))  # 不能直接用sympify，否则会自己造符号

    # [improve_flag]def get_expore->极值点探索：得到表达式后对它使用拉格朗日乘数法，尝试计算可能的极值点
    # 这是实验性方法，需要进一步调整
    def get_expore(f: Expr, sym_str: str = 'x y') -> list:
        """
        求解在无约束下，函数 f(x, y...) 的可能极值点

        参数:
            f: SymPy表达式, 目标函数 f(x, y...)
            sym_str: 参与求解的未知数，用空格分隔
        返回:
            可能的极值点列表 [(x1, y1...), (x2, y2...), ...]
        """
        # 定义符号变量
        xs = symbols(sym_str, real=True)
        # 求偏导并构造方程组
        eqs=[Eq(diff(f,x),0) for x in xs] # ∂L/∂x = 0
        # 解方程组
        solutions=solve(eqs, xs, dict=True)
        # 提取(x, y...)的解（去掉λ)
        extrema=[]
        for sol in solutions:
            if sol:
                xs_val=(sol.get(x,x) for x in xs) # 若x不存在,保留符号x
                extrema.append(tuple(xs_val))
        return extrema
    # ═══════════════════════════════════════════════════════
    # 第四部分：添加对象（add_* 系列）
    # ═══════════════════════════════════════════════════════

    def add_symbol(self, name: str, domain_settings: Optional[DomainSettings] = None):
        """添加并初始化未知数（3D 版不改）"""
        self._add_math_obj(GCSymbol(name, domain_settings))
        self.symbol_names.append(name)

    def add_point(self, name: str, x_str: str, y_str: str, z_str: str, line1: str, line2: str) -> None:
        """
        尝试添加点，并相应地添加依赖关系
        前端会发来 6 个字符串，其中 3 个坐标（x/y/z）和 2 个直线是有内容的
        :param name: 点名称
        :param x_str: 横坐标的字符串表达式，若为 x 则设未知数
        :param y_str: 纵坐标的字符串表达式，若为 y 则设未知数
        :param z_str: 竖坐标的字符串表达式，若为 z 则设未知数 ← 3D 新增
        :param line1: 该点所在的平面/直线 1
        :param line2: 该点所在的平面/直线 2
        """
        # 抄 2D 原版 add_point，做三处修改：
        #   1. 加 z_str 处理（z_str == 'z' → add_symbol(f'z_{name}')）
        #   2. 点在"直线"上：2D 是 _get_line(l).equation()（Ax+By+C=0 一个方程）
        #      3D 直线需要两个平面方程联立，或直接用 SymPy Line3D 的方程（参数式）
        #   3. solve(eqs, x, y, z) 解三元
        # 2D 原版关键结构（抄的时候保持）：
        #   try:
        #       eqs = []
        #       # 设未知数 + 收集方程 + 解出坐标
        #       solution = solve(eqs, x, y, dict=True)[0]
        #       point = GCPoint(name, solution[x], solution[y])
        #       self._add_math_obj(point); self.point_names.append(name)
        #   except Exception as e:
        #       # 清理可能添加的未知数 + 清空 tracker + raise
        try:
            eqs: list[Eq] = []
            required_by_new_symbols: set[str] = set()

            # 设未知数
            if x_str == 'x':
                self.add_symbol(f'x_{name}')
            if y_str == 'y':
                self.add_symbol(f'y_{name}')
            if z_str == 'z':
                self.add_symbol(f'z_{name}')

            # 先设完未知数再读取处理，防止干扰依赖关系
            if x_str != '':
                if x_str == 'x':
                    eqs.append(Eq(x, self._get_sp_symbol(f'x_{name}')))
                    required_by_new_symbols.add(f'x_{name}')
                else:
                    eqs.append(Eq(x, self._eval_str_expr(x_str)))
            if y_str != '':
                if y_str == 'y':
                    eqs.append(Eq(y, self._get_sp_symbol(f'y_{name}')))
                    required_by_new_symbols.add(f'y_{name}')
                else:
                    eqs.append(Eq(y, self._eval_str_expr(y_str)))
            if z_str != '':
                if z_str == 'z':
                    eqs.append(Eq(z, self._get_sp_symbol(f'z_{name}')))
                    required_by_new_symbols.add(f'z_{name}')
                else:
                    eqs.append(Eq(z, self._eval_str_expr(z_str)))

            for l in [line1, line2]:
                if l != '':
                    eqs.append(self._get_line(l).equation())

            # 求解点坐标并添加
            _ans = solve(eqs, x, y, z, dict=True)[0]
            point = GCPoint(name, _ans[x], _ans[y], _ans[z])
            # 反向添加设的未知数对点的依赖，这样在删除点时该点的未知数也会被删除
            point.required_by |= required_by_new_symbols
            self._add_math_obj(point)
            self.point_names.append(name)

        except Exception as e:
            # 清理可能添加的未知数
            for name in (f'x_{name}', f'y_{name}'):
                if name in self.symbol_names:
                    self.symbol_names.remove(name)
                    del self.math_objs[name]
            self.requirements_tracker.clear()
            raise e

    # ═══════════════════════════════════════════════════════
    # 第五部分：条件方法 ★ 2D 有 9 种，3D 你要扩展
    # 每个方法都被 @AddBinCond/@AddUnaryCond 装饰，只负责"给出方程列表"
    # ═══════════════════════════════════════════════════════

    # 新增：内部向量关系方程
    def _vec_eq(self,a: Matrix,b: Matrix, p: int = 0) -> Eq:
        left = a.dot(b) if bool(p) else a.cross(b).norm()**2
        return Eq(left,0)

    @AddBinCond('=')
    def add_expr_eq(self, input1: str, input2: str):
        """两表达式相等（3D 版不改）"""
        return [Eq(self._eval_str_expr(input1), self._eval_str_expr(input2))]

    # 2D 原版的平行/垂直是用一般式系数（a1*b2 == a2*b1）——3D 里要换成方向向量！
    @AddBinCond(r'\\parallel')
    def add_line_parallel_line(self, input1: str, input2: str):
        """线线平行：方向向量叉积 = 0"""
        v1 = self._get_vec(input1); v2 = self._get_vec(input2)
        return [self._vec_eq(v1,v2)]

    @AddBinCond(r'\\perp')
    def add_line_perp_line(self, input1: str, input2: str):
        """线线垂直：方向向量点积 = 0"""
        v1 = self._get_vec(input1); v2 = self._get_vec(input2)
        return [self._vec_eq(v1,v2,1)]

    # 面面平行：法向量叉积 = 0；面面垂直：法向量点积 = 0
    @AddBinCond(r'\\parallel')
    def add_plane_parallel_plane(self, input1: str, input2: str):
        """面面平行：方向向量叉积 = 0"""
        v1 = self._get_plane_normal(input1); v2 = self._get_plane_normal(input2)
        return [self._vec_eq(v1,v2)]

    @AddBinCond(r'\\perp')
    def add_plane_perp_plane(self, input1: str, input2: str):
        """面面垂直：方向向量点积 = 0"""
        v1 = self._get_plane_normal(input1); v2 = self._get_plane_normal(input2)
        return [self._vec_eq(v1,v2,1)]
    # 线面平行：方向·法 = 0；线面垂直：方向∥法（叉积=0）
    @AddBinCond(r'\\parallel')
    def add_line_parallel_plane(self, input1: str, input2: str):
        """线面平行：方向向量叉积 = 0"""
        v1 = self._get_vec(input1); v2 = self._get_plane_normal(input2)
        return [self._vec_eq(v1,v2,1)]

    @AddBinCond(r'\\perp')
    def add_line_perp_plane(self, input1: str, input2: str):
        """线面垂直：方向向量点积 = 0"""
        v1 = self._get_vec(input1); v2 = self._get_plane_normal(input2)
        return [self._vec_eq(v1,v2)]
    # [improve_flag]几何元素集合关系处理

    # ═══════════════════════════════════════════════════════
    # 第六部分：查询 / 删除 / 存取（抄 2D 原版，几乎不改）
    # ═══════════════════════════════════════════════════════

    def get_symbol_names(self) -> list[str]:
        return self.symbol_names

    def get_point_names(self) -> list[str]:
        return self.point_names

    def get_cond_ids(self) -> list[str]:
        return self.cond_ids

    def get_symbols_latex(self) -> list[LatexItem]:
        """
        获取需要在前端页面上展示的符号的 LaTeX，包含取值范围（含始末 $ $）
        相同取值范围的符号会被并到一起
        :return: 一个列表，每项为一个字典（对象）
                 id: 取值范围的 LaTeX，用于前端 ``v-for`` 的 ``key``
                 latex: 该取值范围的完整的 LaTeX
        """
        # 将每个符号名挂到其取值范围上
        domain_names_dict: dict[str, list[str]] = {}
        for name in self.symbol_names:
            gc_symbol: GCSymbol = self.math_objs[name]  # type: ignore
            name_latex = gc_symbol.get_name_latex()
            domain_latex = gc_symbol.get_domain_latex()
            if domain_latex not in domain_names_dict:
                domain_names_dict[domain_latex] = []
            domain_names_dict[domain_latex].append(name_latex)
    
        # 生成结果
        result = []
        for domain, names in domain_names_dict.items():
            result.append({
                'id': domain,
                'latex': fr"$ \displaystyle {', '.join(names)} \in {domain} $"
            })
    
        return result

    def get_points_latex(self):
        """获取所有点的 LaTeX（3D 版点的 LaTeX 是三元组，但本方法逻辑不变）"""
        result = []
        for name in self.point_names:
            result.append({
                'id': name,
                'latex': fr'$ \displaystyle {self.math_objs[name].get_latex()} $'  # type: ignore
            })
        return result

    def get_conds_latex(self):
        """获取所有条件的 LaTeX（原始 + 方程，本方法逻辑不变）"""
        result = []
        for cond_id in self.cond_ids:
            cond: Cond = self.math_objs[cond_id]  # type: ignore
            result.append({
                'id': fr'$$ {cond.get_raw_latex()} $$',
                'latex': cond.get_eqs_latex()
            })
        return result

    def get_deeply_required_by(self, identifier: str) -> list[str]:
        """查询一个对象被哪些对象依赖（含后代，BFS）—— 抄 2D 原版，一字不改"""
        # BFS
        result = set()
        visited = {identifier}
        queue = deque([identifier])
        
        while len(queue) > 0:
            current_id = queue.popleft()
            for i in self.math_objs[current_id].required_by:
                if i not in visited:
                    result.add(i)
                    visited.add(i)
                    queue.append(i)
        
        return list(result)

    def del_objs(self, ids: list[str]) -> None:
        """删除对象及其依赖关系 —— 抄 2D 原版，一字不改"""
        for i in ids:
            # 删除对象
            del self.math_objs[i]
            # 列表除名
            for l in [self.symbol_names, self.point_names, self.cond_ids]:
                if i in l:
                    l.remove(i)
        # 删除依赖关系
        for obj in self.math_objs.values():
            obj.required_by -= set(ids)

    # 纠正原TODO计划，新增读写3D pickle文件方法
    def save_to_file(self) -> None:
        path = windows[0].create_file_dialog(FileDialog.SAVE, file_types=('几何计算器 pickle 文件 (*.gc.pkl)',))
        if path is not None:
            path = path[0]
            with open(path, 'wb') as f:
                pickle.dump(self, f)

    def load_from_file(self) -> None:
        path = windows[0].create_file_dialog(FileDialog.OPEN, file_types=('几何计算器 pickle 文件 (*.gc.pkl)',))
        if path is not None:
            path = path[0]
            with open(path, 'rb') as f:
                self.__dict__ = pickle.load(f).__dict__
    # ═══════════════════════════════════════════════════════
    # 第七部分：🚀 求解（这是最终目标，结构抄 2D 原版）
    # ═══════════════════════════════════════════════════════

    def solve(self, expr: str) -> list[str]:
        """
        🚀 启动！
        :param expr: 要求解的目标的字符串表达式（如 AB、angABC、VABCD）
        :return: 所有可能的解的 LaTeX
        """
        left = to_raw_latex(expr)
        
        target = Symbol('target')
        eqs = [Eq(target, self._eval_str_expr(expr))]
        for i in self.cond_ids:
            eqs.extend(self.math_objs[i].eqs)  # type: ignore
        symbols = [target] + [self.math_objs[i].sp_symbol for i in self.symbol_names]  # type: ignore
        solutions = solve(eqs, symbols, dict=True)
        
        # 关于 ``sqrtdenest``：https://github.com/zhdbk3/GeometryCalculator/issues/5
        result = set(simplify(sqrtdenest(s[target])) for s in solutions)
        result = [f'{left} = {latex(i)}' for i in result]
        return result
