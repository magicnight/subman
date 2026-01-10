"""
历史数据模块 - 记录和分析订阅支出趋势
"""
import pandas as pd
from pathlib import Path
from datetime import datetime
from typing import Optional
import streamlit as st

from ..config import DATA_DIR, CSV_ENCODING


# 历史数据文件路径
HISTORY_FILE = DATA_DIR / "history.csv"

# 历史数据列定义
HISTORY_COLUMNS = [
    '日期',           # 记录日期 (YYYY-MM-DD)
    '订阅总数',       # 当时的订阅总数
    '月均总支出',     # 月均总支出
    '年度预估',       # 年度预估支出
    'AI支出',         # AI 类服务月均支出
    '视频支出',       # 视频类服务月均支出
    '软件支出',       # 软件类服务月均支出
    '系统支出',       # 系统类服务月均支出
    '其他支出'        # 其他类服务月均支出
]


def load_history() -> pd.DataFrame:
    """
    加载历史数据
    
    Returns:
        pd.DataFrame: 历史数据框
    """
    try:
        if not HISTORY_FILE.exists():
            # 创建空的历史文件
            df = pd.DataFrame(columns=HISTORY_COLUMNS)
            df.to_csv(HISTORY_FILE, index=False, encoding=CSV_ENCODING)
            return df
        
        df = pd.read_csv(HISTORY_FILE, encoding=CSV_ENCODING)
        df['日期'] = pd.to_datetime(df['日期'])
        return df
        
    except Exception as e:
        st.warning(f"⚠️ 加载历史数据失败: {e}")
        return pd.DataFrame(columns=HISTORY_COLUMNS)


def save_history(df: pd.DataFrame) -> bool:
    """
    保存历史数据
    
    Args:
        df: 历史数据框
        
    Returns:
        bool: 保存是否成功
    """
    try:
        save_df = df.copy()
        save_df['日期'] = pd.to_datetime(save_df['日期']).dt.strftime('%Y-%m-%d')
        save_df.to_csv(HISTORY_FILE, index=False, encoding=CSV_ENCODING)
        return True
    except Exception as e:
        st.error(f"❌ 保存历史数据失败: {e}")
        return False


def record_monthly_snapshot(subscriptions_df: pd.DataFrame) -> bool:
    """
    记录月度快照
    
    Args:
        subscriptions_df: 当前订阅数据框
        
    Returns:
        bool: 记录是否成功
    """
    if subscriptions_df.empty:
        return False
    
    today = datetime.now().date()
    
    # 检查是否已有当月记录
    history_df = load_history()
    if not history_df.empty:
        history_df['月份'] = pd.to_datetime(history_df['日期']).dt.to_period('M')
        current_month = pd.Period(today, freq='M')
        if current_month in history_df['月份'].values:
            # 更新当月记录而非新增
            mask = history_df['月份'] == current_month
            history_df = history_df[~mask]
        history_df = history_df.drop(columns=['月份'])
    
    # 计算各类支出
    category_expenses = subscriptions_df.groupby('服务性质')['月均成本'].sum()
    
    # 创建新记录
    new_record = {
        '日期': today.strftime('%Y-%m-%d'),
        '订阅总数': len(subscriptions_df),
        '月均总支出': subscriptions_df['月均成本'].sum(),
        '年度预估': subscriptions_df['月均成本'].sum() * 12,
        'AI支出': category_expenses.get('AI', 0),
        '视频支出': category_expenses.get('视频', 0),
        '软件支出': category_expenses.get('软件', 0),
        '系统支出': category_expenses.get('系统', 0),
        '其他支出': category_expenses.get('其他', 0) + 
                   category_expenses.get('音乐', 0)  # 归入其他
    }
    
    # 添加新记录
    new_row = pd.DataFrame([new_record])
    updated_df = pd.concat([history_df, new_row], ignore_index=True)
    
    return save_history(updated_df)


def get_expense_trend(months: int = 12) -> pd.DataFrame:
    """
    获取支出趋势数据
    
    Args:
        months: 获取最近多少个月的数据
        
    Returns:
        pd.DataFrame: 趋势数据
    """
    history_df = load_history()
    
    if history_df.empty:
        return pd.DataFrame()
    
    # 按日期排序并取最近 N 个月
    history_df = history_df.sort_values('日期', ascending=False).head(months)
    history_df = history_df.sort_values('日期')
    
    return history_df


def get_category_trend(category: str, months: int = 12) -> pd.DataFrame:
    """
    获取指定类别的支出趋势
    
    Args:
        category: 服务类别 (AI/视频/软件/系统/其他)
        months: 获取最近多少个月的数据
        
    Returns:
        pd.DataFrame: 类别趋势数据
    """
    history_df = get_expense_trend(months)
    
    if history_df.empty:
        return pd.DataFrame()
    
    column_map = {
        'AI': 'AI支出',
        '视频': '视频支出',
        '软件': '软件支出',
        '系统': '系统支出',
        '其他': '其他支出'
    }
    
    column = column_map.get(category)
    if column and column in history_df.columns:
        return history_df[['日期', column]]
    
    return pd.DataFrame()


def calculate_growth_rate() -> Optional[float]:
    """
    计算月度支出环比增长率
    
    Returns:
        float: 增长率（百分比），如最近月无数据则返回 None
    """
    history_df = get_expense_trend(2)
    
    if len(history_df) < 2:
        return None
    
    current = history_df.iloc[-1]['月均总支出']
    previous = history_df.iloc[-2]['月均总支出']
    
    if previous == 0:
        return None
    
    growth_rate = ((current - previous) / previous) * 100
    return round(growth_rate, 2)
