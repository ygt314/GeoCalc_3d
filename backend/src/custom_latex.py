"""3D几何计算器 - 自定义 LaTeX 打印器

为什么需要它?
  默认情况下,SymPy 把列向量 Matrix([x, y, z]) 打印成:
    \\left[\\begin{matrix}x\\\\y\\\\z\\end{matrix}\\right]   ← 方括号矩阵,丑
  数学惯例中,向量坐标应该写成圆括号:
    \\left( x, y, z \\right)                                ← 想要的样子

  这个模块通过 monkeypatch sympy.latex,让所有 latex() 调用
  都使用 CustomLatexPrinter —— 它把列向量(形状 n×1)改成圆括号输出。

原版参考: https://zhdbk3.github.io/2025/07/14/sympy-customize-latex/
"""

from sympy.printing.latex import LatexPrinter, print_function
import sympy


class CustomLatexPrinter(LatexPrinter):
    def _print_MatrixBase(self, expr):
        # 列向量(只有 1 列)→ 圆括号坐标形式: \left( x, y, z \right)
        if expr.shape[1] == 1:
            return fr"\left( {', '.join(map(self.doprint, expr))} \right)"
        else:
            # 其他矩阵(如 3x3)保持默认
            return super()._print_MatrixBase(expr)


@print_function(CustomLatexPrinter)
def custom_latex(expr, **settings):
    return CustomLatexPrinter(settings).doprint(expr)


def override_latex():
    """全局覆盖 sympy.latex,让所有 latex() 调用走自定义打印器"""
    sympy.latex = custom_latex
