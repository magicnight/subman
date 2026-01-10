"""
统计分析组件 - 可视化订阅数据
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from ..config import CURRENCY_SYMBOL
from ..utils.history import (
    load_history,
    record_monthly_snapshot,
    get_expense_trend,
    calculate_growth_rate
)


def render_analytics(df: pd.DataFrame):
    """
    渲染统计分析页面
    
    Args:
        df: 订阅数据框
    """
    if df.empty:
        st.warning("📭 暂无数据可分析")
        return
    
    st.title("📈 统计分析")
    st.markdown("---")
    
    # 支出构成饼图
    render_expense_pie_chart(df)
    
    st.markdown("---")
    
    # 订阅类型分布
    render_subscription_type_chart(df)
    
    st.markdown("---")
    
    # 历史趋势图（新增）
    render_trend_chart()
    
    st.markdown("---")
    
    # 付费时间线
    render_timeline_chart(df)
    
    # 记录快照按钮
    st.markdown("---")
    render_snapshot_section(df)


def render_expense_pie_chart(df: pd.DataFrame):
    """渲染支出构成饼图"""
    st.markdown("### 💸 按服务类型的月均支出分布")
    
    # 按服务性质分组
    category_expenses = df.groupby('服务性质')['月均成本'].sum().reset_index()
    category_expenses = category_expenses.sort_values('月均成本', ascending=False)
    
    # 创建饼图
    fig = px.pie(
        category_expenses,
        values='月均成本',
        names='服务性质',
        title='',
        hole=0.4,  # 甜甜圈图
        color_discrete_sequence=px.colors.qualitative.Set3
    )
    
    # 自定义样式
    fig.update_traces(
        textposition='inside',
        textinfo='percent+label',
        hovertemplate='<b>%{label}</b><br>月均: ' + CURRENCY_SYMBOL + '%{value:.2f}<br>占比: %{percent}<extra></extra>'
    )
    
    fig.update_layout(
        showlegend=True,
        height=400,
        margin=dict(t=30, b=30, l=30, r=30)
    )
    
    st.plotly_chart(fig, width="stretch")
    
    # 数据表格
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 📊 详细数据")
        display_df = category_expenses.copy()
        display_df['占比'] = (display_df['月均成本'] / display_df['月均成本'].sum() * 100).round(1)
        display_df['月均成本'] = display_df['月均成本'].apply(lambda x: f"{CURRENCY_SYMBOL}{x:.2f}")
        display_df['占比'] = display_df['占比'].apply(lambda x: f"{x}%")
        
        st.dataframe(
            display_df,
            hide_index=True,
            width="stretch"
        )
    
    with col2:
        st.markdown("#### 💡 洞察")
        
        # 找出最大支出类型
        max_category = category_expenses.iloc[0]
        max_percentage = (max_category['月均成本'] / category_expenses['月均成本'].sum()) * 100
        
        st.info(f"""
        **主要支出**: {max_category['服务性质']}
        - 月均: {CURRENCY_SYMBOL}{max_category['月均成本']:.2f}
        - 占比: {max_percentage:.1f}%
        """)
        
        # 服务数量统计
        category_count = df['服务性质'].value_counts()
        st.write(f"**服务数量分布**:")
        for cat, count in category_count.items():
            st.write(f"- {cat}: {count} 个")


def render_subscription_type_chart(df: pd.DataFrame):
    """渲染订阅类型分布柱状图"""
    st.markdown("### 🔄 订阅周期分布")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # 数量分布
        type_count = df['订阅类型'].value_counts().reset_index()
        type_count.columns = ['订阅类型', '数量']
        
        fig = px.bar(
            type_count,
            x='订阅类型',
            y='数量',
            title='订阅数量分布',
            color='订阅类型',
            text='数量'
        )
        
        fig.update_traces(textposition='outside')
        fig.update_layout(
            showlegend=False,
            height=300,
            margin=dict(t=30, b=30, l=30, r=30)
        )
        
        st.plotly_chart(fig, width="stretch")
    
    with col2:
        # 支出分布
        type_expense = df.groupby('订阅类型')['月均成本'].sum().reset_index()
        type_expense.columns = ['订阅类型', '月均成本']
        
        fig = px.bar(
            type_expense,
            x='订阅类型',
            y='月均成本',
            title='月均支出分布',
            color='订阅类型',
            text='月均成本'
        )
        
        fig.update_traces(
            texttemplate=CURRENCY_SYMBOL + '%{text:.2f}',
            textposition='outside'
        )
        fig.update_layout(
            showlegend=False,
            height=300,
            margin=dict(t=30, b=30, l=30, r=30)
        )
        
        st.plotly_chart(fig, width="stretch")


def render_trend_chart():
    """渲染历史趋势图"""
    st.markdown("### 📊 支出趋势分析")
    
    history_df = get_expense_trend(12)
    
    if history_df.empty:
        st.info("📭 暂无历史数据。点击下方「记录当前快照」按钮开始追踪支出趋势。")
        return
    
    # 创建趋势折线图
    fig = go.Figure()
    
    # 月均总支出趋势
    fig.add_trace(go.Scatter(
        x=history_df['日期'],
        y=history_df['月均总支出'],
        mode='lines+markers',
        name='月均总支出',
        line=dict(color='#FF4B4B', width=3),
        marker=dict(size=8),
        hovertemplate='%{x}<br>月均支出: ' + CURRENCY_SYMBOL + '%{y:.2f}<extra></extra>'
    ))
    
    fig.update_layout(
        title='月均支出趋势',
        xaxis_title='日期',
        yaxis_title=f'支出 ({CURRENCY_SYMBOL})',
        height=350,
        hovermode='x unified',
        margin=dict(t=40, b=30, l=30, r=30)
    )
    
    st.plotly_chart(fig, width="stretch")
    
    # 增长率指标
    growth_rate = calculate_growth_rate()
    if growth_rate is not None:
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                label="📈 环比增长",
                value=f"{growth_rate:+.1f}%",
                delta=f"{'上涨' if growth_rate > 0 else '下降'}"
            )
        
        with col2:
            if len(history_df) > 0:
                latest = history_df.iloc[-1]
                st.metric(
                    label="📊 订阅总数",
                    value=f"{int(latest['订阅总数'])} 个"
                )
        
        with col3:
            if len(history_df) > 0:
                latest = history_df.iloc[-1]
                st.metric(
                    label="💰 年度预估",
                    value=f"{CURRENCY_SYMBOL}{latest['年度预估']:.0f}"
                )
    
    # 分类趋势（可展开）
    with st.expander("📋 查看分类支出趋势"):
        if all(col in history_df.columns for col in ['AI支出', '视频支出', '软件支出']):
            fig2 = go.Figure()
            
            colors = {'AI支出': '#FF6B6B', '视频支出': '#4ECDC4', '软件支出': '#45B7D1', '系统支出': '#96CEB4'}
            
            for col in ['AI支出', '视频支出', '软件支出', '系统支出']:
                if col in history_df.columns:
                    fig2.add_trace(go.Scatter(
                        x=history_df['日期'],
                        y=history_df[col],
                        mode='lines+markers',
                        name=col.replace('支出', ''),
                        line=dict(color=colors.get(col, '#666'))
                    ))
            
            fig2.update_layout(
                title='分类支出趋势',
                height=300,
                margin=dict(t=40, b=30, l=30, r=30)
            )
            
            st.plotly_chart(fig2, width="stretch")


def render_timeline_chart(df: pd.DataFrame):
    """渲染时间轴图表"""
    st.markdown("### 📅 付费时间线")
    
    # 筛选未来 90 天内的付费事件
    future_df = df[df['剩余天数'] >= 0].copy()
    future_df = future_df.sort_values('下次付费时间')
    
    if future_df.empty:
        st.info("📭 未来 90 天内无到期订阅")
        return
    
    # 创建甘特图风格的时间线
    fig = go.Figure()
    
    for idx, row in future_df.iterrows():
        fig.add_trace(go.Scatter(
            x=[row['下次付费时间'], row['下次付费时间']],
            y=[0, 1],
            mode='lines+markers+text',
            name=row['名称'],
            text=[row['名称'], f"{CURRENCY_SYMBOL}{row['金额']:.2f}"],
            textposition='top center',
            marker=dict(
                size=15,
                color='red' if row['自动续费'] else 'blue',
                symbol='circle'
            ),
            line=dict(width=2),
            hovertemplate=f"<b>{row['名称']}</b><br>" +
                         f"日期: {row['下次付费时间'].strftime('%Y-%m-%d')}<br>" +
                         f"金额: {CURRENCY_SYMBOL}{row['金额']:.2f}<br>" +
                         f"剩余: {row['剩余天数']} 天<br>" +
                         f"自动续费: {'是' if row['自动续费'] else '否'}<extra></extra>"
        ))
    
    fig.update_layout(
        title='未来付费时间线',
        xaxis_title='日期',
        showlegend=False,
        height=400,
        hovermode='closest',
        yaxis=dict(visible=False)
    )
    
    st.plotly_chart(fig, width="stretch")
    
    # 图例说明
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("🔴 **红色** = 自动续费")
    with col2:
        st.markdown("🔵 **蓝色** = 不自动续费")


def render_snapshot_section(df: pd.DataFrame):
    """渲染快照记录区域"""
    st.markdown("### 📸 数据快照")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.write("记录当前的订阅支出数据作为历史快照，用于追踪长期支出趋势。")
        st.caption("建议每月记录一次快照")
    
    with col2:
        if st.button("📸 记录当前快照", type="primary"):
            if record_monthly_snapshot(df):
                st.success("✅ 快照记录成功！")
                st.rerun()
            else:
                st.error("❌ 记录失败")

