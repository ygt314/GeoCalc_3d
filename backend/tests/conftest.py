"""backend/tests/ 的 pytest 配置

本目录管 src 顶层模块(problem.py、vec_parse_utils.py、custom_latex.py 等)。
src/data/ 的测试在 src/data/tests/ 目录,不在本目录。

无需额外配置: pyproject.toml 的 [tool.pytest.ini_options] 已设置
  - pythonpath = ["src"]  → 测试能 import problem/data 等
  - testpaths = ["tests", "src/data/tests"]  → 两处自动收集
"""
