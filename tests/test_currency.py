"""
测试汇率转换模块
"""
import pytest
from decimal import Decimal
from pathlib import Path
import sys

# 添加项目根目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.utils.currency import (
    convert_to_thb,
    convert_from_thb,
    get_currency_symbol,
    format_currency,
    SUPPORTED_CURRENCIES,
    CURRENCY_SYMBOLS,
    FALLBACK_RATES
)


class TestCurrencyConversion:
    """测试货币转换功能"""
    
    def test_convert_thb_to_thb(self):
        """测试 THB 转 THB（不变）"""
        assert convert_to_thb(100.0, 'THB') == 100.0
    
    def test_convert_usd_to_thb(self):
        """测试 USD 转 THB"""
        result = convert_to_thb(100.0, 'USD')
        # 应该大于原值（因为 USD 对 THB 汇率大于 1）
        assert result > 100.0
    
    def test_convert_from_thb_to_thb(self):
        """测试 THB 转 THB（不变）"""
        assert convert_from_thb(100.0, 'THB') == 100.0
    
    def test_convert_from_thb_to_usd(self):
        """测试 THB 转 USD"""
        result = convert_from_thb(3550.0, 'USD')
        # 应该小于原值（因为 USD 对 THB 汇率大于 1）
        assert result < 3550.0


class TestCurrencySymbols:
    """测试货币符号功能"""
    
    def test_get_thb_symbol(self):
        """测试获取泰铢符号"""
        assert get_currency_symbol('THB') == '฿'
    
    def test_get_usd_symbol(self):
        """测试获取美元符号"""
        assert get_currency_symbol('USD') == '$'
    
    def test_get_unknown_currency_symbol(self):
        """测试获取未知货币符号（返回货币代码）"""
        assert get_currency_symbol('XXX') == 'XXX'
    
    def test_format_currency(self):
        """测试货币格式化"""
        result = format_currency(1234.56, 'THB')
        assert '฿' in result
        assert '1,234.56' in result


class TestSupportedCurrencies:
    """测试支持的货币配置"""
    
    def test_supported_currencies_not_empty(self):
        """测试支持货币列表不为空"""
        assert len(SUPPORTED_CURRENCIES) > 0
    
    def test_thb_in_supported_currencies(self):
        """测试 THB 在支持列表中"""
        assert 'THB' in SUPPORTED_CURRENCIES
    
    def test_major_currencies_supported(self):
        """测试主要货币都被支持"""
        major_currencies = ['USD', 'EUR', 'GBP', 'JPY', 'CNY']
        for currency in major_currencies:
            assert currency in SUPPORTED_CURRENCIES
    
    def test_fallback_rates_have_thb(self):
        """测试备用汇率包含 THB"""
        assert 'THB' in FALLBACK_RATES
        assert FALLBACK_RATES['THB'] == Decimal('1.0')


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
