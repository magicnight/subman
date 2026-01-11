"""
订阅列表组件 - 显示和管理订阅数据
"""
import streamlit as st
import pandas as pd
from datetime import datetime

from ..utils import delete_subscription, update_subscription, load_service_types, load_subscribe_types
from ..utils.currency import get_currency_symbol


def render_subscription_table(df: pd.DataFrame):
    """
    渲染订阅列表表格
    
    Args:
        df: 订阅数据框
    """
    if df.empty:
        st.warning("📭 暂无订阅数据")
        return
    
    st.title("📋 订阅列表")
    st.markdown("---")
    
    # 筛选和排序选项
    render_filters(df)
    
    # 数据展示
    display_df = prepare_display_dataframe(df)
    
    # 移动端提示
    st.info("📱 移动端提示：左右滑动查看完整表格")
    
    # 使用 Streamlit 的数据编辑器
    st.dataframe(
        display_df,
        width='stretch',
        hide_index=True,
        column_config={
            "名称": st.column_config.TextColumn("服务名称", width="medium"),
            "服务性质": st.column_config.TextColumn("类型", width="small"),
            "订阅类型": st.column_config.TextColumn("周期", width="small"),
            "金额": st.column_config.TextColumn(
                "金额",
                width="small"
            ),
            "月均成本": st.column_config.TextColumn(
                "月均",
                width="small"
            ),
            "下次付费时间": st.column_config.DateColumn(
                "下次扣费",
                format="YYYY-MM-DD",
                width="medium"
            ),
            "剩余天数": st.column_config.NumberColumn(
                "剩余天数",
                width="small"
            ),
            "自动续费": st.column_config.CheckboxColumn(
                "自动续费",
                width="small"
            ),
        }
    )
    
    # 管理操作区域
    st.markdown("---")
    
    # 使用标签页组织编辑和删除功能
    tab1, tab2 = st.tabs(["✏️ 编辑订阅", "🗑️ 删除订阅"])
    
    with tab1:
        render_edit_section(df)
    
    with tab2:
        render_delete_section(df)


def render_filters(df: pd.DataFrame):
    """渲染筛选和排序选项（移动端优化）"""
    # 移动端：垂直堆叠；桌面端：3列布局
    # 使用 CSS 媒体查询自动适配，这里保持代码简洁
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # 服务类型筛选
        categories = ['全部'] + sorted(df['服务性质'].unique().tolist())
        selected_category = st.selectbox("🏷️ 服务类型", categories)
        
        if selected_category != '全部':
            st.session_state['filter_category'] = selected_category
        else:
            st.session_state['filter_category'] = None
    
    with col2:
        # 续费状态筛选
        renewal_options = {
            '全部': None,
            '自动续费': True,
            '不续费': False
        }
        selected_renewal = st.selectbox("🔄 续费状态", list(renewal_options.keys()))
        st.session_state['filter_renewal'] = renewal_options[selected_renewal]
    
    with col3:
        # 排序选项
        sort_options = {
            '剩余天数（升序）': ('剩余天数', True),
            '剩余天数（降序）': ('剩余天数', False),
            '月均成本（升序）': ('月均成本', True),
            '月均成本（降序）': ('月均成本', False),
            '名称（A-Z）': ('名称', True),
        }
        selected_sort = st.selectbox("🔢 排序方式", list(sort_options.keys()))
        st.session_state['sort_by'], st.session_state['sort_asc'] = sort_options[selected_sort]


def prepare_display_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """
    准备用于显示的数据框
    
    Args:
        df: 原始数据框
        
    Returns:
        pd.DataFrame: 处理后的数据框
    """
    display_df = df.copy()
    
    # 应用筛选
    if st.session_state.get('filter_category'):
        display_df = display_df[display_df['服务性质'] == st.session_state['filter_category']]
    
    if st.session_state.get('filter_renewal') is not None:
        display_df = display_df[display_df['自动续费'] == st.session_state['filter_renewal']]
    
    # 应用排序
    if st.session_state.get('sort_by'):
        display_df = display_df.sort_values(
            by=st.session_state['sort_by'],
            ascending=st.session_state.get('sort_asc', True)
        )
    
    # 格式化金额列，使用每条订阅实际的货币符号
    def format_amount_with_currency(row, amount_col):
        currency = row.get('货币', 'THB') if pd.notna(row.get('货币')) else 'THB'
        symbol = get_currency_symbol(currency)
        return f"{symbol}{row[amount_col]:.2f}"
    
    display_df['金额'] = display_df.apply(
        lambda row: format_amount_with_currency(row, '金额'), axis=1
    )
    display_df['月均成本'] = display_df.apply(
        lambda row: format_amount_with_currency(row, '月均成本'), axis=1
    )
    
    # 选择要显示的列
    display_columns = [
        '名称',
        '服务性质',
        '订阅类型',
        '金额',
        '月均成本',
        '下次付费时间',
        '剩余天数',
        '自动续费'
    ]
    
    return display_df[display_columns]


def render_edit_section(df: pd.DataFrame):
    """渲染编辑订阅区域"""
    from ..utils.currency import SUPPORTED_CURRENCIES, get_currency_symbol
    
    # 选择要编辑的订阅
    subscription_names = df['名称'].tolist()
    selected_name = st.selectbox(
        "选择要编辑的订阅",
        subscription_names,
        key="edit_select"
    )
    
    if selected_name:
        # 获取当前选中订阅的数据
        index = df[df['名称'] == selected_name].index[0]
        current_data = df.loc[index]
        
        # 使用动态 key，确保每次选择变化时表单完全重建
        form_key = f"edit_subscription_form_{selected_name}"
        with st.form(form_key):
            col1, col2 = st.columns(2)
            
            with col1:
                new_name = st.text_input(
                    "服务名称",
                    value=current_data['名称']
                )
                
                service_types = load_service_types()
                current_service_idx = service_types.index(current_data['服务性质']) if current_data['服务性质'] in service_types else 0
                new_service = st.selectbox(
                    "服务性质",
                    service_types,
                    index=current_service_idx
                )
                
                new_amount = st.number_input(
                    "金额",
                    value=float(current_data['金额']),
                    min_value=0.0,
                    step=0.01,
                    format="%.2f"
                )
                
                # 货币选择
                current_currency = current_data.get('货币', 'THB') if pd.notna(current_data.get('货币', 'THB')) else 'THB'
                current_currency_idx = SUPPORTED_CURRENCIES.index(current_currency) if current_currency in SUPPORTED_CURRENCIES else 0
                new_currency = st.selectbox(
                    "货币",
                    SUPPORTED_CURRENCIES,
                    index=current_currency_idx
                )
            
            with col2:
                supplier_value = current_data.get('供应商', '') if pd.notna(current_data.get('供应商', '')) else ''
                new_supplier = st.text_input(
                    "供应商",
                    value=supplier_value
                )
                
                subscribe_types = load_subscribe_types()
                current_type_idx = subscribe_types.index(current_data['订阅类型']) if current_data['订阅类型'] in subscribe_types else 0
                new_cycle = st.selectbox(
                    "订阅类型",
                    subscribe_types,
                    index=current_type_idx
                )
                
                # 处理日期
                current_date = current_data['下次付费时间']
                if isinstance(current_date, pd.Timestamp):
                    current_date = current_date.date()
                new_date = st.date_input(
                    "下次付费时间",
                    value=current_date
                )
            
            new_auto_renew = st.checkbox(
                "自动续费",
                value=bool(current_data['自动续费'])
            )
            
            # 提交按钮
            submitted = st.form_submit_button("💾 保存修改", type="primary")
            
            if submitted:
                updated_data = {
                    '名称': new_name,
                    '供应商': new_supplier,
                    '服务性质': new_service,
                    '订阅类型': new_cycle,
                    '金额': new_amount,
                    '货币': new_currency,
                    '下次付费时间': new_date.strftime('%Y-%m-%d'),
                    '自动续费': new_auto_renew
                }
                
                if update_subscription(index, updated_data):
                    st.success(f"✅ 成功更新订阅: {new_name}")
                    st.rerun()
                else:
                    st.error("❌ 更新失败，请重试")


def render_delete_section(df: pd.DataFrame):
    """渲染删除订阅区域"""
    col1, col2 = st.columns([3, 1])
    
    with col1:
        # 选择要删除的订阅
        subscription_names = df['名称'].tolist()
        selected_name = st.selectbox(
            "选择要删除的订阅",
            subscription_names,
            key="delete_select"
        )
    
    with col2:
        st.write("")  # 占位符对齐
        st.write("")  # 占位符对齐
        if st.button("🗑️ 删除", type="secondary", key="delete_btn"):
            # 获取索引
            index = df[df['名称'] == selected_name].index[0]
            
            # 确认删除
            if st.session_state.get('confirm_delete') != selected_name:
                st.session_state['confirm_delete'] = selected_name
                st.warning(f"⚠️ 确定要删除 **{selected_name}** 吗？再次点击确认删除。")
            else:
                # 执行删除
                if delete_subscription(index):
                    st.success(f"✅ 已删除 **{selected_name}**")
                    st.session_state['confirm_delete'] = None
                    st.rerun()
                else:
                    st.error("❌ 删除失败")

