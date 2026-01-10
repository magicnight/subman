"""
MySub Manager - 主应用入口
"""
import streamlit as st
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.config import STREAMLIT_CONFIG, CURRENCY_SYMBOL
from src.utils import (
    load_subscriptions,
    load_service_types,
    load_subscribe_types,
    add_subscription
)
from src.components import (
    render_dashboard,
    render_subscription_table,
    render_analytics
)


def main():
    """主函数"""
    # 页面配置
    st.set_page_config(**STREAMLIT_CONFIG)
    
    # 自定义 CSS
    st.markdown("""
    <style>
    .main > div {
        padding-top: 2rem;
    }
    .stAlert {
        margin-top: 1rem;
        margin-bottom: 1rem;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # 侧边栏 - 导航和新增功能
    render_sidebar()
    
    # 加载数据
    df = load_subscriptions()
    
    # 根据选择的页面渲染内容
    page = st.session_state.get('page', '仪表盘')
    
    if page == '仪表盘':
        render_dashboard(df)
    elif page == '订阅列表':
        render_subscription_table(df)
    elif page == '统计分析':
        render_analytics(df)


def render_sidebar():
    """渲染侧边栏"""
    with st.sidebar:
        st.title("📊 MySub Manager")
        st.markdown("---")
        
        # 导航菜单
        st.markdown("### 📑 导航")
        pages = {
            '📊 仪表盘': '仪表盘',
            '📋 订阅列表': '订阅列表',
            '📈 统计分析': '统计分析'
        }
        
        for label, page_name in pages.items():
            if st.button(label, width="stretch", key=f"nav_{page_name}"):
                st.session_state['page'] = page_name
                st.rerun()
        
        st.markdown("---")
        
        # 新增订阅表单
        render_add_form()
        
        st.markdown("---")
        
        # 应用信息
        st.markdown("### ℹ️ 关于")
        st.info("""
        **MySub Manager** v1.0
        
        个人订阅管理助手
        
        让每一笔订阅都清晰可见 💡
        """)
        
        # 数据统计
        df = load_subscriptions()
        if not df.empty:
            total_monthly = df['月均成本'].sum()
            st.markdown(f"""
            **当前概览**:
            - 订阅数: {len(df)} 个
            - 月均支出: {CURRENCY_SYMBOL}{total_monthly:.2f}
            """)


def render_add_form():
    """渲染新增订阅表单"""
    from src.utils.currency import SUPPORTED_CURRENCIES, get_currency_symbol
    
    st.markdown("### ➕ 添加订阅")
    
    with st.form("add_subscription_form", clear_on_submit=True):
        # 基本信息
        name = st.text_input("服务名称 *", placeholder="例如: Netflix")
        supplier = st.text_input("供应商", placeholder="例如: Netflix Inc.")
        
        # 分类信息
        col1, col2 = st.columns(2)
        with col1:
            service_types = load_service_types()
            service = st.selectbox("服务性质 *", service_types)
        
        with col2:
            subscribe_types = load_subscribe_types()
            cycle = st.selectbox("订阅类型 *", subscribe_types)
        
        # 财务信息
        col3, col4, col5 = st.columns([2, 1, 2])
        with col3:
            amount = st.number_input(
                "金额 *",
                min_value=0.0,
                step=0.01,
                format="%.2f"
            )
        
        with col4:
            # 货币选择
            currency = st.selectbox(
                "货币",
                SUPPORTED_CURRENCIES,
                index=0  # 默认 THB
            )
        
        with col5:
            next_date = st.date_input("下次付费时间 *")
        
        # 自动续费
        auto_renew = st.checkbox("自动续费", value=False)
        
        # 提交按钮
        submitted = st.form_submit_button("✅ 添加订阅", width="stretch")
        
        if submitted:
            # 验证必填字段
            if not name:
                st.error("❌ 请输入服务名称")
            elif amount <= 0:
                st.error("❌ 金额必须大于 0")
            else:
                # 构建数据
                new_subscription = {
                    '名称': name,
                    '供应商': supplier if supplier else '',
                    '服务性质': service,
                    '订阅类型': cycle,
                    '金额': amount,
                    '货币': currency,
                    '下次付费时间': next_date.strftime('%Y-%m-%d'),
                    '自动续费': auto_renew
                }
                
                # 添加订阅
                if add_subscription(new_subscription):
                    st.success(f"✅ 成功添加订阅: {name}")
                    st.rerun()
                else:
                    st.error("❌ 添加失败，请重试")


if __name__ == "__main__":
    main()
