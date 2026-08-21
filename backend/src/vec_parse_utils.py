"""3D几何计算器 - 向量解析工具

两个工具，都与维度相关（3D 变化点已标注）：

1. mark_vec_coord: 把用户输入里的坐标二元组/三元组标记为向量。
   2D 版把 (1, 2) 变成 Matrix([1, 2])，3D 版要处理 (1, 2, 3)。
   原版的算法是"找逗号，向左向右配对括号"，理论上逗号数量变了也能处理，
   且验证测试三元组通过！

2. Infix + dot: Python 运算符重载实现的"中缀点乘"。
   它让你能写 a @ dot @ b 来表示 a·b（向量点积）。
   原理：
     __rmatmul__ 在 a @ dot 时被调用（因为 dot 在右边，Python 找不到
     a.__matmul__ 的匹配就尝试右边操作数的反向方法）→ 返回 Infix 包装函数
     __matmul__ 在 (a @ dot) @ b 时被调用 → 执行真正的点积

3. 叉积也支持
"""

from typing import Callable
from sympy import Expr, Matrix
from sympy.matrices import MatrixKind

def mark_vec_coord(expr: str) -> str:
    """用 ``Matrix([])`` 标记表达式中向量的坐标表示，经测试原版也支持多元组"""
    char_list = list(expr)
        # 找出所有逗号
    comma_indexes = [i for i, c in enumerate(char_list) if c == ',']
    for comma_i in comma_indexes:
        # 向左找出未闭合的左括号
        n = 1
        for i in range(comma_i, -1, -1):
            if char_list[i] == ')':
                n += 1
            elif char_list[i] == '(':
                n -= 1
                if n == 0:
                    char_list[i] = 'Matrix(['
                    break
        # 向右找出未闭合的右括号
        n = 1
        for i in range(comma_i, len(char_list)):
            if char_list[i] == '(':
                n += 1
            elif char_list[i] == ')':
                n -= 1
                if n == 0:
                    char_list[i] = '])'
                    break
    return ''.join(char_list)


def expr_to_list(f: Expr|Matrix, choice: str=''):
    '''提取向量坐标，用于解析'''
    # 判断向量: Matrix 用 isinstance;SymPy Expr 用 .kind(如 MatrixSymbol 是 MatrixKind)
    # 注意: Matrix 对象本身没有 .kind 属性,不能直接 f.kind
    print('[debug]:class is Matrix',isinstance(f, Matrix))
    a = [i for i in f] if isinstance(f, Matrix) or (hasattr(f, 'kind') and isinstance(f.kind, MatrixKind)) else [f]
    if choice == 'expr': return a if len(a)==1 else []
    elif choice == 'matrix': return [] if len(a)==1 else a
    return a


class Infix:
    """【Python 竟然允许这种语法， Python中缀运算符】 https://www.bilibili.com/video/BV1Xe411r7VE"""

    def __init__(self, func: Callable):
        self.func = func

    def __rmatmul__(self, other) -> 'Infix':
        return Infix(lambda var: self.func(other, var))

    def __matmul__(self, other):
        return self.func(other)

# 点积
dot = Infix(lambda a, b: a.dot(b))
# 叉积
cross = Infix(lambda a,b: a.cross(b))
