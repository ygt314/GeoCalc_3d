"""3D几何计算器 - 数学对象抽象基类

与 2D 原版完全相同，一个字都不用改。
它定义了三类对象（符号/点/条件）的公共契约：
  - 每个对象有唯一 id（字符串）
  - 每个对象记录"被谁依赖"（required_by）

学习要点：required_by 是整张依赖图的边。为什么是"被谁依赖"而不是"依赖谁"？
因为删除对象时要问"删掉我会连累谁"，而"我依赖谁"在添加时就确定了（通过
requirements_tracker 记录）。方向反过来的设计会让删除逻辑很痛苦。
"""

from abc import ABC


class MathObj(ABC):
    """
    数学对象（未知数、点、条件等）的抽象类

    :ivar id: 每个数学对象都有唯一的 ``id``
    :ivar required_by: 该对象被哪些对象直接依赖，存放它们的 ``id``
    """

    def __init__(self, identifier: str):
        self.id = identifier
        self.required_by: set[str] = set()

    def add_required_by(self, obj: 'MathObj') -> None:
        """记录 obj 依赖本对象（本对象被 obj 引用）"""
        self.required_by.add(obj.id)
