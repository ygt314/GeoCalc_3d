"""GCSymbol 未知数 —— 完整测试面

✅ 已实现,全部测试通过(2026-08-03 实现)

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

    def test_default_is_real(self):
        """不传 settings → 默认 R"""
        latex_str, assumptions = get_domain_latex_and_assumptions(None)
        assert latex_str == r'\mathbb{R}'
        assert assumptions == {'real': True}


class TestSymbolInit:
    """GCSymbol 初始化契约"""

    def test_init_basic(self):
        """普通符号:id 是名字,sp_symbol 是 SymPy 符号"""
        s = GCSymbol('a')
        assert s.id == 'a'
        assert s.sp_symbol.name == 'a'

    def test_domain_applied(self):
        """带取值范围:正数 → sp_symbol 有 positive 假设"""
        s = GCSymbol('a', {'negative': False, 'zero': False, 'positive': True})
        assert s.sp_symbol.is_positive is True

    def test_point_coord_symbol(self):
        """点坐标未知数(形如 x_A)也能创建"""
        s = GCSymbol('x_A')
        assert s.id == 'x_A'


class TestSymbolDisplay:
    """符号 LaTeX 展示契约"""

    def test_name_latex(self):
        s = GCSymbol('a')
        assert s.get_name_latex() == 'a'

    def test_domain_latex(self):
        s = GCSymbol('a', {'negative': False, 'zero': False, 'positive': True})
        assert s.get_domain_latex() == r'(0, +\infty)'
