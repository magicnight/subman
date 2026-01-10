"""
导出模块 - 生成订阅报告 PDF/Excel
"""
import io
from datetime import datetime
from typing import Optional
import pandas as pd
import streamlit as st

from ..config import CURRENCY_SYMBOL, PAGE_TITLE


def export_to_excel(df: pd.DataFrame) -> bytes:
    """
    导出订阅数据为 Excel 格式
    
    Args:
        df: 订阅数据框
        
    Returns:
        bytes: Excel 文件的字节数据
    """
    # 准备导出数据
    export_df = df.copy()
    
    # 格式化日期
    if '下次付费时间' in export_df.columns:
        export_df['下次付费时间'] = pd.to_datetime(export_df['下次付费时间']).dt.strftime('%Y-%m-%d')
    
    # 格式化布尔值
    if '自动续费' in export_df.columns:
        export_df['自动续费'] = export_df['自动续费'].map({True: '是', False: '否'})
    
    # 选择导出列
    export_columns = [
        '名称', '供应商', '服务性质', '订阅类型',
        '金额', '月均成本', '下次付费时间', '剩余天数', '自动续费'
    ]
    export_df = export_df[[col for col in export_columns if col in export_df.columns]]
    
    # 创建 Excel 文件
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        export_df.to_excel(writer, sheet_name='订阅列表', index=False)
        
        # 添加汇总表
        summary_data = {
            '指标': ['订阅总数', '月均总支出', '年度预估支出', '自动续费数', '即将到期数'],
            '数值': [
                f"{len(df)} 个",
                f"{CURRENCY_SYMBOL}{df['月均成本'].sum():.2f}",
                f"{CURRENCY_SYMBOL}{df['月均成本'].sum() * 12:.2f}",
                f"{df['自动续费'].sum()} 个",
                f"{len(df[df['剩余天数'].between(0, 7)])} 个"
            ]
        }
        summary_df = pd.DataFrame(summary_data)
        summary_df.to_excel(writer, sheet_name='汇总统计', index=False)
    
    return output.getvalue()


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


def generate_text_report(df: pd.DataFrame) -> str:
    """
    生成纯文本报告
    
    Args:
        df: 订阅数据框
        
    Returns:
        str: 报告文本
    """
    now = datetime.now()
    
    lines = [
        "=" * 60,
        f"📊 {PAGE_TITLE} - 订阅报告",
        "=" * 60,
        f"生成时间: {now.strftime('%Y-%m-%d %H:%M')}",
        "",
        "📈 概览统计",
        "-" * 40,
        f"  订阅总数: {len(df)} 个",
        f"  月均支出: {CURRENCY_SYMBOL}{df['月均成本'].sum():.2f}",
        f"  年度预估: {CURRENCY_SYMBOL}{df['月均成本'].sum() * 12:.2f}",
        f"  自动续费: {df['自动续费'].sum()} 个",
        "",
        "💸 按类型支出",
        "-" * 40,
    ]
    
    # 按服务类型统计
    category_expenses = df.groupby('服务性质')['月均成本'].sum().sort_values(ascending=False)
    for category, amount in category_expenses.items():
        percentage = (amount / df['月均成本'].sum()) * 100
        lines.append(f"  {category}: {CURRENCY_SYMBOL}{amount:.2f} ({percentage:.1f}%)")
    
    lines.extend([
        "",
        "📋 订阅详情",
        "-" * 40,
    ])
    
    # 订阅列表
    for _, row in df.sort_values('剩余天数').iterrows():
        status = "⚠️" if row['剩余天数'] <= 7 and row['自动续费'] else "  "
        auto = "🔄" if row['自动续费'] else "  "
        lines.append(
            f"{status}{auto} {row['名称']:<20} "
            f"{CURRENCY_SYMBOL}{row['金额']:>10.2f} "
            f"({row['订阅类型']}) "
            f"剩余{row['剩余天数']:>3}天"
        )
    
    lines.extend([
        "",
        "=" * 60,
        f"报告生成于 {PAGE_TITLE}",
        "=" * 60,
    ])
    
    return "\n".join(lines)


def generate_markdown_report(df: pd.DataFrame) -> str:
    """
    生成 Markdown 格式报告
    
    Args:
        df: 订阅数据框
        
    Returns:
        str: Markdown 报告
    """
    now = datetime.now()
    total_monthly = df['月均成本'].sum()
    
    md = f"""# 📊 {PAGE_TITLE} - 订阅报告

**生成时间**: {now.strftime('%Y-%m-%d %H:%M')}

---

## 📈 概览统计

| 指标 | 数值 |
|------|------|
| 订阅总数 | {len(df)} 个 |
| 月均支出 | {CURRENCY_SYMBOL}{total_monthly:.2f} |
| 年度预估 | {CURRENCY_SYMBOL}{total_monthly * 12:.2f} |
| 自动续费 | {df['自动续费'].sum()} 个 |
| 即将到期 | {len(df[df['剩余天数'].between(0, 7)])} 个 |

---

## 💸 按类型支出分布

| 类型 | 月均支出 | 占比 |
|------|----------|------|
"""
    
    # 按服务类型统计
    category_expenses = df.groupby('服务性质')['月均成本'].sum().sort_values(ascending=False)
    for category, amount in category_expenses.items():
        percentage = (amount / total_monthly) * 100
        md += f"| {category} | {CURRENCY_SYMBOL}{amount:.2f} | {percentage:.1f}% |\n"
    
    md += f"""
---

## 📋 订阅列表

| 服务名称 | 类型 | 金额 | 周期 | 下次付费 | 剩余天数 | 自动续费 |
|---------|------|------|------|---------|---------|---------|
"""
    
    for _, row in df.sort_values('剩余天数').iterrows():
        auto = "✅" if row['自动续费'] else "❌"
        warning = "⚠️" if row['剩余天数'] <= 7 else ""
        date_str = row['下次付费时间'].strftime('%Y-%m-%d') if hasattr(row['下次付费时间'], 'strftime') else str(row['下次付费时间'])[:10]
        md += f"| {warning}{row['名称']} | {row['服务性质']} | {CURRENCY_SYMBOL}{row['金额']:.2f} | {row['订阅类型']} | {date_str} | {row['剩余天数']} | {auto} |\n"
    
    md += f"""
---

> 报告由 **{PAGE_TITLE}** 生成
"""
    
    return md


def render_export_buttons(df: pd.DataFrame):
    """
    渲染导出按钮组
    
    Args:
        df: 订阅数据框
    """
    st.markdown("### 📥 导出报告")
    
    col1, col2, col3 = st.columns(3)
    
    now = datetime.now().strftime('%Y%m%d')
    
    with col1:
        # Excel 导出
        excel_data = export_to_excel(df)
        st.download_button(
            label="📊 下载 Excel",
            data=excel_data,
            file_name=f"subscriptions_{now}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    
    with col2:
        # CSV 导出
        csv_data = export_to_csv(df)
        st.download_button(
            label="📄 下载 CSV",
            data=csv_data,
            file_name=f"subscriptions_{now}.csv",
            mime="text/csv"
        )
    
    with col3:
        # Markdown 报告
        md_report = generate_markdown_report(df)
        st.download_button(
            label="📝 下载 Markdown",
            data=md_report,
            file_name=f"subscription_report_{now}.md",
            mime="text/markdown"
        )
