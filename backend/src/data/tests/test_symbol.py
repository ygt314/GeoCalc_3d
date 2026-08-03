"""GCSymbol 未知数 —— 完整测试面

⚠️ 注意:get_domain_latex_and_assumptions 和 GCSymbol.__init__ 是 TODO(待你实现)。
这里按"契约测试"的方式写好预期行为,用 xfail 标记。
【你实现后:删除 @pytest.mark.xfail 装饰器,测试就会转绿】

覆盖:
  - 取值范围 → (LaTeX, SymPy 假设) 映射(6 种组合 + 默认)
  - GCSymbol 初始化(id / domain_latex / sp_symbol)
  - 符号展示
"""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from data.symbol import get_domain_latex_and_assumptions, GCSymbol  # noqa: E402


class TestDomainMapping:
    """取值范围 → (LaTeX, SymPy assumptions) 契约
    前端勾选 [负, 零, 正] 三项 → 对应的 LaTeX 和 SymPy 假设
    """

    @pytest.mark.xfail(reason='TODO: 待实现 get_domain_latex_and_assumptions', strict=False)
    @pytest.mark.parametrize('negative, zero, positive, expected_latex, expected_assumption', [
        # 全勾 = R
        (True, True, True, r'\mathbb{R}', {'real': True}),
        # 只负
        (True, False, False, r'(-\infty, 0)', {'negative': True}),
        # 负+零
        (True, True, False, r'(-\infty, 0]', {'nonpositive': True}),
        # 只正
        (False, False, True, r'(0, +\infty)', {'positive': True}),
        # 零+正
        (False, True, True, r'[0, +\infty)', {'nonnegative': True}),
        # 负+正(非零)
        (True, False, True, r'(-\infty, 0) \cup (0, +\infty)', {'nonzero': True}),
    ])
    def test_domain(self, negative, zero, positive, expected_latex, expected_assumption):
        settings = {'negative': negative, 'zero': zero, 'positive': positive}
        latex_str, assumptions = get_domain_latex_and_assumptions(settings)
        assert latex_str == expected_latex
        assert assumptions == expected_assumption

    @pytest.mark.xfail(reason='TODO: 待实现 get_domain_latex_and_assumptions', strict=False)
    def test_default_is_real(self):
        """不传 settings → 默认 R"""
        latex_str, assumptions = get_domain_latex_and_assumptions(None)
        assert latex_str == r'\mathbb{R}'
        assert assumptions == {'real': True}


class TestSymbolInit:
    """GCSymbol 初始化契约"""

    @pytest.mark.xfail(reason='TODO: 待实现 GCSymbol.__init__', strict=False)
    def test_init_basic(self):
        """普通符号:id 是名字,sp_symbol 是 SymPy 符号"""
        s = GCSymbol('a')
        assert s.id == 'a'
        assert s.sp_symbol.name == 'a'

    @pytest.mark.xfail(reason='TODO: 待实现 GCSymbol.__init__', strict=False)
    def test_domain_applied(self):
        """带取值范围:正数 → sp_symbol 有 positive 假设"""
        s = GCSymbol('a', {'negative': False, 'zero': False, 'positive': True})
        assert s.sp_symbol.is_positive is True

    @pytest.mark.xfail(reason='TODO: 待实现 GCSymbol.__init__', strict=False)
    def test_point_coord_symbol(self):
        """点坐标未知数(形如 x_A)也能创建"""
        s = GCSymbol('x_A')
        assert s.id == 'x_A'


class TestSymbolDisplay:
    """符号 LaTeX 展示契约"""

    @pytest.mark.xfail(reason='TODO: 待实现 GCSymbol(依赖 __init__)', strict=False)
    def test_name_latex(self):
        s = GCSymbol('a')
        assert s.get_name_latex() == 'a'

    @pytest.mark.xfail(reason='TODO: 待实现 GCSymbol(依赖 __init__)', strict=False)
    def test_domain_latex(self):
        s = GCSymbol('a', {'negative': False, 'zero': False, 'positive': True})
        assert s.get_domain_latex() == r'(0, +\infty)'
