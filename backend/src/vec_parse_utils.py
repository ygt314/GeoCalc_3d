"""3D几何计算器 - 向量解析工具

两个工具，都与维度相关（3D 变化点已标注）：

1. mark_vec_coord: 把用户输入里的坐标二元组/三元组标记为向量。
   2D 版把 (1, 2) 变成 Matrix([1, 2])，3D 版要处理 (1, 2, 3)。
   原版的算法是"找逗号，向左向右配对括号"，理论上逗号数量变了也能处理，
   但你验证时要测试三元组！

2. Infix + dot: Python 运算符重载实现的"中缀点乘"。
   它让你能写 a @ dot @ b 来表示 a·b（向量点积）。
   原理：
     __rmatmul__ 在 a @ dot 时被调用（因为 dot 在右边，Python 找不到
     a.__matmul__ 的匹配就尝试右边操作数的反向方法）→ 返回 Infix 包装函数
     __matmul__ 在 (a @ dot) @ b 时被调用 → 执行真正的点积

TODO(你来补全)：
  - mark_vec_coord 抄 2D 原版（括号配对逻辑不变，向量变三元组）
  - dot 中缀运算符直接照抄（3D 点积公式不同，但运算符机制完全一样）
"""

from typing import Callable


def mark_vec_coord(expr: str) -> str:
    """用 ``Matrix([])`` 标记表达式中向量的坐标表示"""
    # TODO(你来补全): 抄 2D 原版实现
    # 原版思路：
    #   1. 找所有逗号位置
    #   2. 每个逗号向左找配对的 '(' → 替换成 'Matrix(['（注意嵌套括号计数）
    #   3. 向右找配对的 ')' → 替换成 '])'
    #   4. 返回替换后的字符串
    # 3D 注意：三元组 (1, 2, 3) 有两个逗号，替换逻辑要保证正确配对
    raise NotImplementedError('TODO: 实现 mark_vec_coord')


class Infix:
    """Python 中缀运算符技巧（原版注释引用了 B站视频 BV1Xe411r7VE）"""

    def __init__(self, func: Callable):
        self.func = func

    def __rmatmul__(self, other) -> 'Infix':
        return Infix(lambda var: self.func(other, var))

    def __matmul__(self, other):
        return self.func(other)


# TODO(你来补全): 定义 3D 点积
# 2D 版：dot = Infix(lambda a, b: a.dot(b))
# 3D 版 SymPy 里 Matrix 的 dot 方法对三维同样适用，所以大概率一行不改：
#   dot = Infix(lambda a, b: a.dot(b))
#
# 注意：不要在这里直接 raise —— 否则 import 模块就会崩，无法渐进式开发。
# 先注释掉，等你实现时取消注释即可。
# dot = Infix(lambda a, b: a.dot(b))
