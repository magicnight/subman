"""
测试导出模块
"""
import pytest
import pandas as pd
from datetime import datetime
from pathlib import Path
import sys

# 添加项目根目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.utils.exporter import (
    export_to_excel,
    export_to_csv,
    generate_text_report,
    generate_markdown_report
)


@pytest.fixture
def sample_subscription_df():
    """创建测试用的订阅数据框"""
    return pd.DataFrame({
        '名称': ['Netflix', 'Claude Pro', 'Spotify'],
        '供应商': ['Netflix Inc.', 'Anthropic', 'Spotify AB'],
        '服务性质': ['视频', 'AI', '音乐'],
        '订阅类型': ['月付', '年付', '月付'],
        '金额': [419.0, 7500.0, 149.0],
        '月均成本': [419.0, 625.0, 149.0],
        '下次付费时间': pd.to_datetime(['2026-02-01', '2026-12-01', '2026-02-15']),
        '剩余天数': [21, 324, 35],
        '自动续费': [True, False, True]
    })


class TestExcelExport:
    """测试 Excel 导出功能"""
    
    def test_export_returns_bytes(self, sample_subscription_df):
        """测试导出返回字节数据"""
        result = export_to_excel(sample_subscription_df)
        assert isinstance(result, bytes)
        assert len(result) > 0
    
    def test_export_empty_dataframe(self):
        """测试导出空数据框"""
        empty_df = pd.DataFrame(columns=['名称', '金额', '月均成本', '下次付费时间', '剩余天数', '自动续费'])
        result = export_to_excel(empty_df)
        assert isinstance(result, bytes)


class TestCsvExport:
    """测试 CSV 导出功能"""
    
    def test_export_returns_string(self, sample_subscription_df):
        """测试导出返回字符串"""
        result = export_to_csv(sample_subscription_df)
        assert isinstance(result, str)
        assert len(result) > 0
    
    def test_export_contains_headers(self, sample_subscription_df):
        """测试导出包含列头"""
        result = export_to_csv(sample_subscription_df)
        assert '名称' in result
        assert '金额' in result
    
    def test_export_contains_data(self, sample_subscription_df):
        """测试导出包含数据"""
        result = export_to_csv(sample_subscription_df)
        assert 'Netflix' in result
        assert 'Claude Pro' in result


class TestTextReport:
    """测试文本报告生成"""
    
    def test_report_contains_title(self, sample_subscription_df):
        """测试报告包含标题"""
        result = generate_text_report(sample_subscription_df)
        assert 'MySub Manager' in result
    
    def test_report_contains_statistics(self, sample_subscription_df):
        """测试报告包含统计信息"""
        result = generate_text_report(sample_subscription_df)
        assert '订阅总数' in result
        assert '月均支出' in result
    
    def test_report_contains_subscriptions(self, sample_subscription_df):
        """测试报告包含订阅列表"""
        result = generate_text_report(sample_subscription_df)
        assert 'Netflix' in result


class TestMarkdownReport:
    """测试 Markdown 报告生成"""
    
    def test_report_is_valid_markdown(self, sample_subscription_df):
        """测试报告是有效的 Markdown"""
        result = generate_markdown_report(sample_subscription_df)
        # 检查 Markdown 标题
        assert '# ' in result
        assert '## ' in result
    
    def test_report_contains_table(self, sample_subscription_df):
        """测试报告包含表格"""
        result = generate_markdown_report(sample_subscription_df)
        # Markdown 表格使用 | 分隔
        assert '|' in result
        assert '---' in result
    
    def test_report_contains_statistics(self, sample_subscription_df):
        """测试报告包含统计表格"""
        result = generate_markdown_report(sample_subscription_df)
        assert '概览统计' in result
        assert '订阅总数' in result
    
    def test_report_contains_emoji(self, sample_subscription_df):
        """测试报告包含表情符号"""
        result = generate_markdown_report(sample_subscription_df)
        assert '📊' in result or '📈' in result


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
