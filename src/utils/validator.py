"""
数据验证模块 - 提供订阅数据的验证功能
"""
import pandas as pd
from datetime import datetime
from typing import Optional
from decimal import Decimal, InvalidOperation


class ValidationError(Exception):
    """验证错误异常"""
    pass


def validate_subscription_data(data: dict) -> tuple[bool, Optional[str]]:
    """
    验证订阅数据的完整性和格式
    
    Args:
        data: 订阅数据字典
        
    Returns:
        tuple[bool, Optional[str]]: (是否有效, 错误信息)
    """
    # 必填字段检查
    required_fields = ['名称', '服务性质', '订阅类型', '金额', '下次付费时间']
    
    for field in required_fields:
        if field not in data or data[field] is None or data[field] == '':
            return False, f"缺少必填字段: {field}"
    
    # 名称验证
    if not isinstance(data['名称'], str) or len(data['名称'].strip()) == 0:
        return False, "服务名称不能为空"
    
    if len(data['名称']) > 100:
        return False, "服务名称过长（最多 100 字符）"
    
    # 金额验证
    try:
        amount = float(data['金额'])
        if amount <= 0:
            return False, "金额必须大于 0"
        if amount > 1_000_000:
            return False, "金额超出合理范围"
    except (ValueError, TypeError):
        return False, "金额格式无效"
    
    # 日期验证
    if not validate_date(data['下次付费时间']):
        return False, "日期格式无效，请使用 YYYY-MM-DD 格式"
    
    return True, None


def validate_date(date_value) -> bool:
    """
    验证日期格式是否正确
    
    Args:
        date_value: 日期值（字符串、datetime 或 date）
        
    Returns:
        bool: 是否有效
    """
    if date_value is None:
        return False
    
    # 如果已经是 datetime 类型
    if isinstance(date_value, datetime):
        return True
    
    # 如果是 pandas Timestamp
    if isinstance(date_value, pd.Timestamp):
        return True
    
    # 如果是字符串，尝试解析
    if isinstance(date_value, str):
        try:
            datetime.strptime(date_value, '%Y-%m-%d')
            return True
        except ValueError:
            return False
    
    return False


def validate_amount(amount) -> tuple[bool, float]:
    """
    验证并转换金额
    
    Args:
        amount: 金额值
        
    Returns:
        tuple[bool, float]: (是否有效, 转换后的金额)
    """
    try:
        # 使用 Decimal 避免浮点误差
        decimal_amount = Decimal(str(amount))
        float_amount = float(decimal_amount)
        
        if float_amount <= 0:
            return False, 0.0
        
        return True, round(float_amount, 2)
    except (InvalidOperation, ValueError, TypeError):
        return False, 0.0


def validate_service_type(service_type: str, valid_types: list[str]) -> bool:
    """
    验证服务类型是否在允许列表中
    
    Args:
        service_type: 服务类型
        valid_types: 允许的类型列表
        
    Returns:
        bool: 是否有效
    """
    return service_type in valid_types


def validate_subscribe_type(subscribe_type: str, valid_types: list[str]) -> bool:
    """
    验证订阅类型是否在允许列表中
    
    Args:
        subscribe_type: 订阅类型
        valid_types: 允许的类型列表
        
    Returns:
        bool: 是否有效
    """
    return subscribe_type in valid_types


def validate_dataframe(df: pd.DataFrame, required_columns: list[str]) -> tuple[bool, list[str]]:
    """
    验证 DataFrame 是否包含所有必需列
    
    Args:
        df: 数据框
        required_columns: 必需列列表
        
    Returns:
        tuple[bool, list[str]]: (是否有效, 缺失列列表)
    """
    missing_columns = [col for col in required_columns if col not in df.columns]
    return len(missing_columns) == 0, missing_columns


def sanitize_string(value: str, max_length: int = 255) -> str:
    """
    清理字符串输入
    
    Args:
        value: 输入字符串
        max_length: 最大长度
        
    Returns:
        str: 清理后的字符串
    """
    if not isinstance(value, str):
        value = str(value)
    
    # 去除首尾空白
    value = value.strip()
    
    # 限制长度
    if len(value) > max_length:
        value = value[:max_length]
    
    return value
