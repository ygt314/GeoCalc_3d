"""3D几何计算器 - 核心：Problem 类

这是整个项目的"大脑"。2D 原版 478 行，本文件是骨架 + 详细注释，
核心实现（TODO 标注处）由你对照 2D 原版手写补全 —— 这正是学习的目的。

Problem 的职责（记住这张地图）

  1. 管理所有数学对象：self.math_objs（id → 对象）
  2. 维护依赖图：requirements_tracker + track_requirement（装饰器）
  3. 把用户字符串表达式编译成 SymPy 代码：_eval_str_expr
  4. 把几何条件翻译成代数方程：add_* 系列方法（@AddCond 装饰器）
  5. 求解：solve() —— 把所有方程丢给 SymPy 的 solve

2D → 3D 核心变化清单（你在 TODO 处要做的）

  - 点的坐标从 (x, y) → (x, y, z)，所有 _get_* 方法加 z 分量
  - _get_line（Line2D）→ 线在 3D 里不能再用"一般式 ax+by+c=0"表示！
    3D 直线用：方向向量 + 参数方程，或用 SymPy 的 Line3D
  - 斜率 k / 截距 b 概念在 3D 消失（3D 线没有单一斜率）→ 改用方向向量
  - 新增 _get_plane（平面）、法向量、点面距离、体积等
  - 条件类型扩展：线面平行/垂直、面面平行/垂直、共面、异面、四面体体积…
已知异常:
- 设置实数不能确保Abs,sqrt正常求解,因为sympy.solve内部可能无法正常论证(子)表达式具有实数属性,
失误时会抛NotImplementedError
"""

from custom_latex import override_latex

override_latex()

from typing import Never, Optional, Callable

import functools
from abc import ABC, abstractmethod
# 新增Plane，并为点线适配3D；删除Segment无用项，距离就是模长
# 暂时新增asin适配线面所成角
from sympy import Symbol, Expr, symbols, simplify, Eq, Line3D, solve, Point3D, Plane, Matrix, asin, acos, latex, Abs, sqrtdenest
from sympy import diff, sqrt, sin, cos, tan, pi, Integer  # noqa
from sympy.logic.boolalg import BooleanTrue, BooleanFalse
# 新增叉积cross
from data import MathObj, GCSymbol, GCPoint, Cond, to_raw_latex, to_raw_expr
from type_hints import DomainSettings
from vec_parse_utils import dot, cross, expr_to_list
from data_op import DataOperate

def get_ans(a:Expr|Matrix, b=0):
    '''关于 `sqrtdenest`: https://github.com/zhdbk3/GeometryCalculator/issues/5'''
    if b == 1: return simplify(a)
    elif b == 2: return sqrtdenest(a)
    return simplify(sqrtdenest(a))
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


class Problem(DataOperate):
    def __init__(self):
        super().__init__()
        # 用于临时存放正在添加的新对象依赖哪些对象
        self.requirements_tracker: set[MathObj] = set()
        # 最近一次 solve 解出的目标表达式
        # 对"解"探索而非对原始输入表达式,仅存当前结果,换题即覆盖)
        self._last_exprs: dict[str, Expr] = {}
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
    # get point
    @track_requirement
    def _get_x_of(self, name: str):
        """x"""
        return self.math_objs[name].x  # type: ignore

    @track_requirement
    def _get_y_of(self, name: str):
        """y"""
        return self.math_objs[name].y  # type: ignore
    @track_requirement
    def _get_z_of(self, name: str):
        """z"""
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
        """平面法向量"""
        return Matrix(self._get_plane(name[1:4]).normal_vector)
    
    def _get_angv(self, vv: str) -> Expr:
        """angvABCD 向量夹角 <AB,CD> [0, pi)"""
        v1 = self._get_vec(vv[0:2])
        v2 = self._get_vec(vv[2:])
        return acos(v1.dot(v2) / (v1.norm() * v2.norm()))

    def _get_angr(self, m: str,l: str,n: str) -> Expr:
        """angrABCD 二面角 ∠A-BC-D [0, pi)"""
        v1 = self._get_plane_normal('p'+m+l)
        v2 = self._get_plane_normal('p'+n+l)
        return acos(v1.dot(v2) / (v1.norm() * v2.norm()))

    def _get_angc(self,a: str,b: str) -> Expr:
        """angcAB_CD 所成角 AB与CD [0, pi/2]"""
        vn = lambda x:self._get_vec(x) if len(x)==2 else self._get_plane_normal('p'+x[0:3])
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
    def _eval_str_expr(self, expr: str) -> Expr | Matrix | Never:
        """
        尝试解析字符串表达式，解析失败会报错
        原理：一串正则替换把"人话"变成 Python 代码，然后 eval
        """
        expr = to_raw_expr(expr)
        return simplify(eval(expr))  # 不能直接用sympify，否则会自己造符号
    # 极值点探索:得到表达式后对每个变量求偏导 = 0,解方程组求驻点
    def _get_extrema(self, f: Expr, syms: str = 'x y') -> list:
        """
        求解在无约束下,函数 f(x, y...) 的可能极值点(驻点)
        参数:
            f: 待求解函数,sympy表达式
            syms: 参与求解的未知数,用空格分隔(默认 'x y')
        返回:
            驻点列表,每项为Latex结果
        注意:
            - 求的是驻点(偏导=0),不区分极大/极小,需自行判断
            - 只解多项式方程组,复杂函数可能无解或很慢
            - 返回 LaTeX 字符串而非 Expr 对象,因为 pywebview 桥接
              需要 JSON 序列化,SymPy 对象无法序列化
        """
        print("[debug_get_extrema]:f",f'(syms:{syms})')
        print(f)
        # 定义符号变量(symbols('x y') → 元组, symbols('x') → 单个 Symbol,统一转列表)
        xs = symbols(syms, real=True)
        if not isinstance(xs, (tuple, list)):
            xs = [xs]
        extrema = []
        # 求偏导并构造方程组
        eqs = [Eq(diff(f, x_i), 0) for x_i in xs]  # ∂f/∂x = 0
        # 解方程组
        solutions = solve(eqs, xs, dict=True)
        if not solutions:
            return ["\\emptyset"]
        for sol in solutions:
            values = [get_ans(sol.get(x_i, x_i)) for x_i in xs]
            # LaTeX 展示: (x1, y1, ...)
            ans = values + [get_ans(f.subs(sol).expand())]
            extrema.append(latex(tuple(ans)))
        print("[debug_get_extrema]:极值点列表")
        print(extrema)
        return extrema
    # ═══════════════════════════════════════════════════════
    # 第四部分：添加对象（add_* 系列）
    # ═══════════════════════════════════════════════════════
    def add_symbol(self, name: str, domain_settings: Optional[DomainSettings] = None):
        """添加并初始化未知数（3D 版不改）
        防重: 同名符号已存在则报错,避免 solve 时 duplicate symbols 崩溃
        """
        if name in self.math_objs:
            raise ValueError(f'未知数 {name} 已存在!')
        self._add_math_obj(GCSymbol(name, domain_settings))
        self.symbol_names.append(name)

    def _add_gcpoint(self, n: str, x: Expr, y: Expr, z: Expr):
        '''添加点（内部方法）'''
        point = GCPoint(n,x,y,z)
        self._add_math_obj(point)
        self.point_names.append(n)
    def add_O_point(self, name:str):
        '''添加原点'''
        o = Integer(0)
        self.orig_point = name
        self._add_gcpoint(name,o,o,o)
    def add_point_from_move(self,new:str,way:str):
        '''依据DSL语法way确定基点并平移创建新点new'''
        if len(way)<4: return
        xyz,old = way[0],way[1]
        p_str = [way if i==xyz else i+old for i in 'xyz']
        self._add_gcpoint(new,*tuple(self._eval_str_expr(p)
                                    for p in p_str))
    def add_point_from_vec(self,new:str,old:str,way:str):
        '''依据向量平移创建新点new ，基点为空则使用原点'''
        o = old if old else self.orig_point
        if not o: return
        p,v = self._get_sp_point(o),self._eval_str_expr(way)
        x,y,z = Matrix(p)+v
        self._add_gcpoint(new,x,y,z)

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
                    eq = self._get_line(l).equation()
                    # Line3D.equation() 返回 Tuple(两个平面方程联立),2D 是单方程
                    # 判断: 不是 SymPy 表达式(没有 free_symbols 的是 Tuple/容器)
                    # 注意: Tuple 也有 free_symbols 属性!要用 Expr 判断
                    if not isinstance(eq, Expr):
                        for sub_eq in eq:
                            eqs.append(Eq(sub_eq, 0))
                    else:
                        eqs.append(Eq(eq, 0))
            # 求解点坐标并添加
            # 关键: 把本点新建的坐标未知数(x_A/y_A/z_A)也纳入求解,
            # 否则它们是自由符号, solve(x,y,z) 会误判欠定
            solve_symbols = [x, y, z] + [
                self.math_objs[s].sp_symbol for s in required_by_new_symbols  # type: ignore
            ]
            _ans = solve(eqs, solve_symbols, dict=True)[0]
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
    @AddBinCond(r'\parallel')
    def add_line_parallel_line(self, input1: str, input2: str):
        """线线平行：方向向量叉积 = 0"""
        v1 = self._get_vec(input1); v2 = self._get_vec(input2)
        return [self._vec_eq(v1,v2)]

    @AddBinCond(r'\perp')
    def add_line_perp_line(self, input1: str, input2: str):
        """线线垂直：方向向量点积 = 0"""
        v1 = self._get_vec(input1); v2 = self._get_vec(input2)
        return [self._vec_eq(v1,v2,1)]
    # 面面平行：法向量叉积 = 0；面面垂直：法向量点积 = 0
    @AddBinCond(r'\parallel')
    def add_plane_parallel_plane(self, input1: str, input2: str):
        """面面平行：法向量叉积 = 0"""
        v1 = self._get_plane_normal(input1); v2 = self._get_plane_normal(input2)
        return [self._vec_eq(v1,v2)]

    @AddBinCond(r'\perp')
    def add_plane_perp_plane(self, input1: str, input2: str):
        """面面垂直：法向量点积 = 0"""
        v1 = self._get_plane_normal(input1); v2 = self._get_plane_normal(input2)
        return [self._vec_eq(v1,v2,1)]
    # 线面平行：方向·法 = 0；线面垂直：方向∥法（叉积=0）
    @AddBinCond(r'\parallel')
    def add_line_parallel_plane(self, input1: str, input2: str):
        """线面平行：方向向量与法向量点积 = 0"""
        v1 = self._get_vec(input1); v2 = self._get_plane_normal(input2)
        return [self._vec_eq(v1,v2,1)]

    @AddBinCond(r'\perp')
    def add_line_perp_plane(self, input1: str, input2: str):
        """线面垂直：方向向量与法向量叉积 = 0"""
        v1 = self._get_vec(input1); v2 = self._get_plane_normal(input2)
        return [self._vec_eq(v1,v2)]

    # 点与直线的关系省略，添加点支持绑定直线
    @AddBinCond(r'\in')
    def add_point_in_plane(self, p: str, pp: str):
        '''点在平面，可以绕过部分集合运算'''
        # 过点 p 与平面上第一点的直线 ∥ 该平面 → 等价于 p ∈ 平面
        # 注意: 不能调用被 @AddBinCond 装饰的 add_line_parallel_plane
        # (装饰后直接调用会执行添加流程并返回 None),这里写裸方程逻辑
        v1 = self._get_vec(p + pp[1])
        v2 = self._get_plane_normal(pp)
        return [self._vec_eq(v1, v2, 1)]
    # [improve_flag]几何元素集合关系处理
    # ═══════════════════════════════════════════════════════
    # 第七部分：🚀 求解（这是最终目标，结构抄 2D 原版）
    # ═══════════════════════════════════════════════════════
    def _get_target(self,expr_list:list[Expr])->set[tuple[Expr]]:
        '''求解target标记表达式'''
        d=len(expr_list)
        tars = [Symbol(f'target{i}') for i in range(d)]
        eqs = [Eq(tars[i], expr_list[i]) for i in range(d)]
        print('[debug]:总方程')
        for i in self.cond_ids:
            eqs.extend(self.math_objs[i].eqs)  # type: ignore
        symbols = tars + [self.math_objs[i].sp_symbol for i in self.symbol_names]  # type: ignore
        print(eqs)
        print('[debug]:未知数')
        print(symbols)
        solutions = solve(eqs, symbols, dict=True)
        return set(tuple(get_ans(s[tars[i]]) for i in range(d))
                     for s in solutions
                     if tars[-1] in s)

    def solve(self, expr: str) -> list[str]:
        """
        🚀 启动！
        逻辑与 2D 相同，增加求值结果缓存
        :param expr: 要求解的目标的字符串表达式
        :return: 所有可能的解的 LaTeX
        """
        left, right = to_raw_latex(expr), self._eval_str_expr(expr)
        exprs = expr_to_list(right,'expr')
        if not exprs: return ['这是向量哦~小朋友你是不是有很多问号？？？']

        solutions = self._get_target(exprs)
        if not solutions: return ['无解：\\emptyset']
        result = set(t[0] for t in solutions)

        self._last_exprs = {str(latex(i)):i for i in result}
        result = [f'{left} = {latex(i)}' for i in result]
        return result

    def solve_vec(self, expr: str, sure_vec=True) -> list[str]:
        """
        n维向量求解!
        :param expr: 要求解的目标的字符串表达式(结果是向量)
        :return: 所有可能的解的 LaTeX
        """
        left, right = to_raw_latex(expr), self._eval_str_expr(expr)
        exprs = expr_to_list(right,'matrix' if sure_vec else '')
        if not exprs: return ['-\\_-’这不是向量。。。请圆润地回到标量！！！']

        solutions = self._get_target(exprs)
        if not solutions: return ['无解：\\emptyset']

        self._last_exprs = {}
        result = [f'{left} = {latex(i)}' for i in solutions]
        return result
    def solve_mult(self, exprs: str):
        '''
        自动求解多个表达式（兼容单个表达式，但没有缓存）
        exprs:多个表达式之间用,隔开，例如 a,b,c,d或(a,b,c,d)
        不受支持或限制的表达式：
        1.表达式内部有“,”，这可能会导致DSL语法误解，例如 vecAB dot (1,2,3),(1,(2,3),4)
        2.表达式结果是向量，例如 vecAB,m+1
        '''
        return self.solve_vec(f'({exprs})', False)
    # 极值点探索入口，含调试输出（控制台）
    def expore_extrema(self, choice: str, sym_str: str, custom=False)->list:
        '''
        choice:选择对应latex或自定义表达式
        sym_str:待求符号
        custom:是否自定义
        return:极值点latex列表
        '''
        print('[debug]:choice',f'(custom is {custom})')
        print(choice)
        sss=self._eval_str_expr(choice) if custom else self._last_exprs[choice]
        return self._get_extrema(sss,sym_str)
   # 函数值探索入口，含调试输出（控制台）
    def expore_func(self, choice: str, values: dict, custom=False) -> str:
        '''
        choice:选择对应latex或自定义表达式
        sym_str:待求符号
        custom:是否自定义
        return:函数值latex
        '''
        print('[debug]:choice',f'(custom is {custom})')
        print(choice)
        sss=self._eval_str_expr(choice) if custom else self._last_exprs[choice]
        # values 的键是字符串(如 {'t': 2}),需转成与表达式匹配的 SymPy Symbol
        # 注意: _eval_str_expr 创建的符号带 real=True,须用 symbols() 同样生成
        sub_map = {}
        for k, v in values.items():
            sym = symbols(k, real=True)
            sub_map[sym if isinstance(sym, Symbol) else sym[0]] = v
        ans = get_ans(sss.subs(sub_map))
        print('values:',values)
        print("answer:",ans)
        return f"$ {latex(ans)} = {latex(ans.evalf())}$"
