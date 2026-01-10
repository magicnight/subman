"""
仪表盘组件 - 显示订阅概览
"""
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

from ..config import WARNING_DAYS, CURRENCY_SYMBOL
from ..utils.exporter import render_export_buttons
from ..utils.currency import render_rate_status


def render_dashboard(df: pd.DataFrame):
    """
    渲染仪表盘
    
    Args:
        df: 订阅数据框
    """
    if df.empty:
        st.warning("📭 暂无订阅数据，请先添加订阅")
        return
    
    # 标题
    st.title("📊 订阅管理仪表盘")
    
    # 汇率状态（新增）
    render_rate_status()
    
    st.markdown("---")
    
    # 红绿灯预警区
    render_warning_banner(df)
    
    # KPI 指标卡片
    render_kpi_cards(df)
    
    # 快速统计
    render_quick_stats(df)
    
    # 导出报告
    st.markdown("---")
    render_export_buttons(df)


def render_warning_banner(df: pd.DataFrame):
    """渲染到期预警横幅"""
    # 筛选即将到期且自动续费的订阅
    upcoming = df[
        (df['剩余天数'] <= WARNING_DAYS) & 
        (df['剩余天数'] >= 0) & 
        (df['自动续费'] == True)
    ]
    
    if not upcoming.empty:
        st.error(f"""
        🚨 **到期预警** - 您有 {len(upcoming)} 个订阅即将在 {WARNING_DAYS} 天内自动续费！
        """)
        
        with st.expander("📋 查看详情", expanded=True):
            for _, row in upcoming.iterrows():
                col1, col2, col3 = st.columns([2, 1, 1])
                with col1:
                    st.write(f"**{row['名称']}** ({row['服务性质']})")
                with col2:
                    st.write(f"⏰ {row['剩余天数']} 天后")
                with col3:
                    st.write(f"💰 {CURRENCY_SYMBOL}{row['金额']:.2f}")
    else:
        st.success("✅ 近期无需关注的自动续费项目")


def render_kpi_cards(df: pd.DataFrame):
    """渲染 KPI 指标卡片"""
    col1, col2, col3, col4 = st.columns(4)
    
    # 订阅总数
    with col1:
        total_count = len(df)
        active_count = len(df[df['剩余天数'] >= 0])
        st.metric(
            label="📚 订阅总数",
            value=f"{total_count} 个",
            delta=f"{active_count} 个有效"
        )
    
    # 月均总支出
    with col2:
        monthly_total = df['月均成本'].sum()
        st.metric(
            label="💰 月均总支出",
            value=f"{CURRENCY_SYMBOL}{monthly_total:.2f}",
            delta=None
        )
    
    # 年度总支出
    with col3:
        yearly_total = monthly_total * 12
        st.metric(
            label="📅 年度预估",
            value=f"{CURRENCY_SYMBOL}{yearly_total:.2f}",
            delta=None
        )
    
    # 近期预警
    with col4:
        upcoming_count = len(df[
            (df['剩余天数'] <= WARNING_DAYS) & 
            (df['剩余天数'] >= 0) & 
            (df['自动续费'] == True)
        ])
        st.metric(
            label="⚠️ 近期预警",
            value=f"{upcoming_count} 个",
            delta="需关注" if upcoming_count > 0 else "安全"
        )


def render_quick_stats(df: pd.DataFrame):
    """渲染快速统计信息"""
    st.markdown("### 📈 快速统计")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 💸 按服务类型支出")
        category_stats = df.groupby('服务性质')['月均成本'].sum().sort_values(ascending=False)
        
        for category, cost in category_stats.items():
            percentage = (cost / df['月均成本'].sum()) * 100
            st.write(f"**{category}**: {CURRENCY_SYMBOL}{cost:.2f} ({percentage:.1f}%)")
    
    with col2:
        st.markdown("#### 🔄 按订阅类型分布")
        cycle_stats = df['订阅类型'].value_counts()
        
        for cycle, count in cycle_stats.items():
            percentage = (count / len(df)) * 100
            st.write(f"**{cycle}**: {count} 个 ({percentage:.1f}%)")
    
    st.markdown("---")
    
    # 最贵的 3 个订阅
    st.markdown("#### 💎 最贵的订阅")
    top3 = df.nlargest(3, '月均成本')[['名称', '服务性质', '月均成本']]
    
    for idx, row in top3.iterrows():
        st.write(f"🏆 **{row['名称']}** ({row['服务性质']}) - {CURRENCY_SYMBOL}{row['月均成本']:.2f}/月")

