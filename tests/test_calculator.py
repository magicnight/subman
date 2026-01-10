"""
测试数据加载模块
"""
import pytest
import pandas as pd
from pathlib import Path
import sys

# 添加项目根目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.utils.data_loader import calculate_monthly_cost


class TestCalculator:
    """测试财务计算逻辑"""
    
    def test_monthly_cost_monthly_cycle(self):
        """测试月付计算"""
        row = pd.Series({
            '金额': 100.0,
            '订阅类型': '月付'
        })
        assert calculate_monthly_cost(row) == 100.0
    
    def test_monthly_cost_yearly_cycle(self):
        """测试年付计算"""
        row = pd.Series({
            '金额': 1200.0,
            '订阅类型': '年付'
        })
        assert calculate_monthly_cost(row) == 100.0
    
    def test_monthly_cost_quarterly_cycle(self):
        """测试季付计算"""
        row = pd.Series({
            '金额': 300.0,
            '订阅类型': '季付'
        })
        assert calculate_monthly_cost(row) == 100.0
    
    def test_monthly_cost_lifetime(self):
        """测试终身订阅"""
        row = pd.Series({
            '金额': 999.0,
            '订阅类型': '终身'
        })
        assert calculate_monthly_cost(row) == 0.0


class TestDataValidation:
    """测试数据验证逻辑"""
    
    def test_required_columns(self):
        """测试必需列验证"""
        # 这里可以添加更多验证测试
        pass


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
