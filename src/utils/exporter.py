"""
导出模块 - 导出订阅数据为 CSV 格式
"""
from datetime import datetime
import pandas as pd
import streamlit as st

from ..config import CURRENCY_SYMBOL


def export_to_csv(df: pd.DataFrame) -> str:
    """
    导出订阅数据为 CSV 格式
    
    Args:
        df: 订阅数据框
        
    Returns:
        str: CSV 格式的字符串
    """
    export_df = df.copy()
    
    # 格式化日期
    if '下次付费时间' in export_df.columns:
        export_df['下次付费时间'] = pd.to_datetime(export_df['下次付费时间']).dt.strftime('%Y-%m-%d')
    
    # 格式化布尔值
    if '自动续费' in export_df.columns:
        export_df['自动续费'] = export_df['自动续费'].map({True: 'TRUE', False: 'FALSE'})
    
    # 选择导出列
    export_columns = [
        '名称', '供应商', '服务性质', '订阅类型',
        '金额', '月均成本', '下次付费时间', '剩余天数', '自动续费'
    ]
    export_df = export_df[[col for col in export_columns if col in export_df.columns]]
    
    return export_df.to_csv(index=False, encoding='utf-8-sig')


def render_export_buttons(df: pd.DataFrame):
    """
    渲染导出按钮（仅 CSV 格式）
    
    Args:
        df: 订阅数据框
    """
    st.markdown("### 📥 导出数据")
    st.caption("导出订阅数据为 CSV 格式，用于备份或迁移")
    
    now = datetime.now().strftime('%Y%m%d')
    
    # CSV 导出
    csv_data = export_to_csv(df)
    st.download_button(
        label="📄 下载 CSV",
        data=csv_data,
        file_name=f"subscriptions_{now}.csv",
        mime="text/csv",
        width='stretch',
        type="primary"
    )
