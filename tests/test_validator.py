"""
测试数据验证模块
"""
import pytest
from datetime import datetime, date
import pandas as pd
from pathlib import Path
import sys

# 添加项目根目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.utils.validator import (
    ValidationError,
    validate_subscription_data,
    validate_date,
    validate_amount,
    validate_service_type,
    validate_subscribe_type,
    validate_dataframe,
    sanitize_string
)


class TestSubscriptionValidation:
    """测试订阅数据验证"""
    
    def test_valid_subscription_data(self):
        """测试有效的订阅数据"""
        data = {
            '名称': 'Netflix',
            '服务性质': '视频',
            '订阅类型': '月付',
            '金额': 419.0,
            '下次付费时间': '2026-02-01'
        }
        is_valid, error = validate_subscription_data(data)
        assert is_valid is True
        assert error is None
    
    def test_missing_required_field(self):
        """测试缺少必填字段"""
        data = {
            '服务性质': '视频',
            '订阅类型': '月付',
            '金额': 419.0,
            '下次付费时间': '2026-02-01'
        }
        is_valid, error = validate_subscription_data(data)
        assert is_valid is False
        assert '名称' in error
    
    def test_empty_name(self):
        """测试空名称"""
        data = {
            '名称': '   ',
            '服务性质': '视频',
            '订阅类型': '月付',
            '金额': 419.0,
            '下次付费时间': '2026-02-01'
        }
        is_valid, error = validate_subscription_data(data)
        assert is_valid is False
    
    def test_invalid_amount_zero(self):
        """测试金额为零"""
        data = {
            '名称': 'Netflix',
            '服务性质': '视频',
            '订阅类型': '月付',
            '金额': 0,
            '下次付费时间': '2026-02-01'
        }
        is_valid, error = validate_subscription_data(data)
        assert is_valid is False
        assert '金额' in error
    
    def test_invalid_amount_negative(self):
        """测试负金额"""
        data = {
            '名称': 'Netflix',
            '服务性质': '视频',
            '订阅类型': '月付',
            '金额': -100,
            '下次付费时间': '2026-02-01'
        }
        is_valid, error = validate_subscription_data(data)
        assert is_valid is False


class TestDateValidation:
    """测试日期验证"""
    
    def test_valid_date_string(self):
        """测试有效日期字符串"""
        assert validate_date('2026-01-15') is True
    
    def test_valid_datetime(self):
        """测试有效 datetime 对象"""
        assert validate_date(datetime.now()) is True
    
    def test_valid_pandas_timestamp(self):
        """测试有效 pandas Timestamp"""
        assert validate_date(pd.Timestamp.now()) is True
    
    def test_invalid_date_string(self):
        """测试无效日期字符串"""
        assert validate_date('2026/01/15') is False
    
    def test_none_date(self):
        """测试 None 日期"""
        assert validate_date(None) is False


class TestAmountValidation:
    """测试金额验证"""
    
    def test_valid_amount_integer(self):
        """测试有效整数金额"""
        is_valid, amount = validate_amount(100)
        assert is_valid is True
        assert amount == 100.0
    
    def test_valid_amount_float(self):
        """测试有效浮点数金额"""
        is_valid, amount = validate_amount(99.99)
        assert is_valid is True
        assert amount == 99.99
    
    def test_valid_amount_string(self):
        """测试有效字符串金额"""
        is_valid, amount = validate_amount('50.50')
        assert is_valid is True
        assert amount == 50.50
    
    def test_invalid_amount_negative(self):
        """测试负数金额"""
        is_valid, amount = validate_amount(-50)
        assert is_valid is False
    
    def test_invalid_amount_string(self):
        """测试无效字符串金额"""
        is_valid, amount = validate_amount('abc')
        assert is_valid is False


class TestTypeValidation:
    """测试类型验证"""
    
    def test_valid_service_type(self):
        """测试有效服务类型"""
        valid_types = ['AI', '视频', '软件']
        assert validate_service_type('AI', valid_types) is True
    
    def test_invalid_service_type(self):
        """测试无效服务类型"""
        valid_types = ['AI', '视频', '软件']
        assert validate_service_type('其他', valid_types) is False
    
    def test_valid_subscribe_type(self):
        """测试有效订阅类型"""
        valid_types = ['年付', '月付', '季付']
        assert validate_subscribe_type('年付', valid_types) is True


class TestDataFrameValidation:
    """测试 DataFrame 验证"""
    
    def test_valid_dataframe(self):
        """测试有效 DataFrame"""
        df = pd.DataFrame({'A': [1], 'B': [2], 'C': [3]})
        is_valid, missing = validate_dataframe(df, ['A', 'B'])
        assert is_valid is True
        assert missing == []
    
    def test_missing_columns(self):
        """测试缺失列"""
        df = pd.DataFrame({'A': [1]})
        is_valid, missing = validate_dataframe(df, ['A', 'B', 'C'])
        assert is_valid is False
        assert 'B' in missing
        assert 'C' in missing


class TestSanitizeString:
    """测试字符串清理"""
    
    def test_trim_whitespace(self):
        """测试去除首尾空白"""
        result = sanitize_string('  hello  ')
        assert result == 'hello'
    
    def test_max_length(self):
        """测试最大长度限制"""
        result = sanitize_string('abcdefghij', max_length=5)
        assert result == 'abcde'
        assert len(result) == 5
    
    def test_convert_non_string(self):
        """测试非字符串转换"""
        result = sanitize_string(12345)
        assert result == '12345'


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
