"""
数据加载和验证模块
"""
import pandas as pd
from pathlib import Path
from typing import Optional
import streamlit as st

from ..config import (
    SUBSCRIPTIONS_FILE,
    SERVICE_FILE,
    SUBSCRIBE_TYPE_FILE,
    CSV_ENCODING,
    REQUIRED_COLUMNS
)


@st.cache_data(ttl=300)  # 缓存 5 分钟
def load_subscriptions() -> pd.DataFrame:
    """
    加载订阅数据
    
    Returns:
        pd.DataFrame: 订阅数据框
        
    Raises:
        FileNotFoundError: 文件不存在
        ValueError: 数据格式错误
    """
    try:
        df = pd.read_csv(SUBSCRIPTIONS_FILE, encoding=CSV_ENCODING)
        
        # 验证必需列
        missing_cols = set(REQUIRED_COLUMNS) - set(df.columns)
        if missing_cols:
            raise ValueError(f"缺少必需的列: {missing_cols}")
        
        # 数据类型转换
        df['下次付费时间'] = pd.to_datetime(df['下次付费时间'])
        df['金额'] = pd.to_numeric(df['金额'], errors='coerce')
        df['自动续费'] = df['自动续费'].map({'TRUE': True, 'FALSE': False, True: True, False: False})
        
        # 计算衍生字段
        df['剩余天数'] = (df['下次付费时间'] - pd.Timestamp.now()).dt.days
        
        # 计算月均成本
        df['月均成本'] = df.apply(lambda row: calculate_monthly_cost(row), axis=1)
        
        return df
        
    except FileNotFoundError:
        st.error(f"❌ 找不到数据文件: {SUBSCRIPTIONS_FILE}")
        st.info("💡 请确保 data/subscriptions.csv 文件存在")
        return pd.DataFrame()
        
    except Exception as e:
        st.error(f"❌ 加载数据时出错: {str(e)}")
        return pd.DataFrame()


def calculate_monthly_cost(row: pd.Series) -> float:
    """
    计算月均成本（统一转换为泰铢 THB）
    
    Args:
        row: DataFrame 的一行数据
        
    Returns:
        float: 月均成本（THB）
    """
    # 延迟导入避免循环依赖
    from .currency import convert_to_thb
    
    amount = row['金额']
    cycle = row['订阅类型']
    currency = row.get('货币', 'THB')  # 默认使用 THB
    
    # 先将金额转换为泰铢
    amount_thb = convert_to_thb(amount, currency)
    
    # 根据订阅类型计算月均成本
    if cycle == '月付':
        return amount_thb
    elif cycle == '年付':
        return amount_thb / 12
    elif cycle == '季付':
        return amount_thb / 3
    elif cycle == '半年付':
        return amount_thb / 6
    elif cycle == '终身':
        return 0  # 终身订阅不计入月均
    else:
        return amount_thb  # 默认按月付计算


@st.cache_data
def load_service_types() -> list[str]:
    """加载服务类型枚举"""
    try:
        df = pd.read_csv(SERVICE_FILE, encoding=CSV_ENCODING)
        return df['服务性质'].tolist()
    except Exception as e:
        st.warning(f"⚠️ 加载服务类型失败: {e}")
        return ['AI', '视频', '软件', '系统', '其他']


@st.cache_data
def load_subscribe_types() -> list[str]:
    """加载订阅类型枚举"""
    try:
        df = pd.read_csv(SUBSCRIBE_TYPE_FILE, encoding=CSV_ENCODING)
        return df['订阅类型'].tolist()
    except Exception as e:
        st.warning(f"⚠️ 加载订阅类型失败: {e}")
        return ['年付', '月付', '季付']


def save_subscriptions(df: pd.DataFrame) -> bool:
    """
    保存订阅数据到 CSV
    
    Args:
        df: 要保存的数据框
        
    Returns:
        bool: 保存是否成功
    """
    try:
        # 移除计算字段
        save_df = df.drop(columns=['剩余天数', '月均成本'], errors='ignore')
        
        # 格式化日期
        save_df['下次付费时间'] = pd.to_datetime(save_df['下次付费时间']).dt.strftime('%Y-%m-%d')
        
        # 格式化布尔值
        save_df['自动续费'] = save_df['自动续费'].map({True: 'TRUE', False: 'FALSE'})
        
        # 保存文件
        save_df.to_csv(SUBSCRIPTIONS_FILE, index=False, encoding=CSV_ENCODING)
        
        # 清除缓存以重新加载数据
        st.cache_data.clear()
        
        return True
        
    except Exception as e:
        st.error(f"❌ 保存数据失败: {str(e)}")
        return False


def add_subscription(data: dict) -> bool:
    """
    添加新订阅
    
    Args:
        data: 订阅数据字典
        
    Returns:
        bool: 添加是否成功
    """
    try:
        df = load_subscriptions()
        new_row = pd.DataFrame([data])
        updated_df = pd.concat([df, new_row], ignore_index=True)
        return save_subscriptions(updated_df)
        
    except Exception as e:
        st.error(f"❌ 添加订阅失败: {str(e)}")
        return False


def delete_subscription(index: int) -> bool:
    """
    删除订阅
    
    Args:
        index: 要删除的行索引
        
    Returns:
        bool: 删除是否成功
    """
    try:
        df = load_subscriptions()
        updated_df = df.drop(index=index).reset_index(drop=True)
        return save_subscriptions(updated_df)
        
    except Exception as e:
        st.error(f"❌ 删除订阅失败: {str(e)}")
        return False


def update_subscription(index: int, data: dict) -> bool:
    """
    更新订阅信息
    
    Args:
        index: 要更新的行索引
        data: 更新后的订阅数据字典
        
    Returns:
        bool: 更新是否成功
    """
    try:
        df = load_subscriptions()
        
        if index < 0 or index >= len(df):
            st.error("❌ 无效的订阅索引")
            return False
        
        # 更新指定行的数据
        for key, value in data.items():
            if key in df.columns:
                df.at[index, key] = value
        
        return save_subscriptions(df)
        
    except Exception as e:
        st.error(f"❌ 更新订阅失败: {str(e)}")
        return False

