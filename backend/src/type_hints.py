"""3D几何计算器 - 类型提示

原版只有 DomainSettings 和 LatexItem。
3D 版建议新增（等你写的时候决定）：
- PlaneSettings? 平面不需要 settings，方程本身就确定
- 如果你的 DSL 支持更多对象，可以在这里加对应的 TypedDict
"""

from typing import TypedDict


class DomainSettings(TypedDict):
    """未知数的取值范围设置（前端勾选后传过来）
    negative: 可以是负数
    zero:     可以是零
    positive: 可以是正数
    """
    negative: bool
    zero: bool
    positive: bool


class LatexItem(TypedDict):
    """前端展示列表的一项
    id:    用于 v-for 的 key（通常是 LaTeX 字符串本身，天然唯一）
    latex: 展示用的完整 LaTeX（含 $$ 或 $ 定界符）
    """
    id: str
    latex: str
