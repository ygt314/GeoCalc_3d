"""3D几何计算器 - API 桥接层

这是前端 JS 和 Python 后端之间的"桥梁"。
pywebview 的 create_window(js_api=api) 会把 api 实例的方法暴露给前端，
前端 JS 直接调用：window.pywebview.api.add_point(...)

原版里 API 就是个持有 Problem 单例的壳。
3D 版同样不需要改结构 —— 前端能调用的方法由 Problem 里的公共方法决定。

学习要点：为什么用单例？因为前端每次调用都是独立进程空间外的 RPC，
必须保证所有调用操作的是同一个 Problem 实例（同一道题的数学对象集合）。
"""

from logger import frontend_logger
from problem import Problem


class API:
    problem = Problem()   # 唯一的 Problem 实例，整个程序共享
    logger = frontend_logger


api = API()
