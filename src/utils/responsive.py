"""
响应式设计工具 - 移动端优化
"""
import streamlit as st


def get_responsive_css() -> str:
    """
    获取响应式 CSS 样式
    
    Returns:
        str: CSS 样式字符串
    """
    return """
    <style>
    /* 移动端样式优化 (< 768px) */
    @media (max-width: 768px) {
        /* KPI 卡片：4列 → 2列 */
        .element-container [data-testid="column"] {
            flex: 0 0 50% !important;
            max-width: 50% !important;
            width: 50% !important;
        }
        
        /* 减少内边距 */
        .main .block-container {
            padding: 1rem !important;
        }
        
        /* 表格：优化字体和滚动 */
        .dataframe {
            font-size: 0.875rem !important;
        }
        
        /* 按钮：增大点击区域 */
        .stButton > button {
            min-height: 44px !important;
            width: 100% !important;
            font-size: 1rem !important;
        }
        
        /* 输入框：全宽 */
        .stTextInput > div > div > input,
        .stSelectbox > div > div > select,
        .stNumberInput > div > div > input {
            width: 100% !important;
        }
        
        /* 表单字段：单列布局 */
        .stForm .element-container {
            width: 100% !important;
        }
        
        /* 侧边栏：优化间距 */
        .css-1d391kg {
            padding-top: 1rem !important;
        }
    }
    
    /* 小屏幕手机 (< 480px) */
    @media (max-width: 480px) {
        /* KPI 卡片：单列布局 */
        .element-container [data-testid="column"] {
            flex: 0 0 100% !important;
            max-width: 100% !important;
            width: 100% !important;
        }
        
        /* 进一步减少内边距 */
        .main .block-container {
            padding: 0.5rem !important;
        }
        
        /* 标题字体调整 */
        h1 {
            font-size: 1.5rem !important;
        }
        
        h2 {
            font-size: 1.25rem !important;
        }
        
        h3 {
            font-size: 1.1rem !important;
        }
    }
    
    /* 平板设备 (768px - 1024px) */
    @media (min-width: 768px) and (max-width: 1024px) {
        /* KPI 卡片：2列布局 */
        .element-container [data-testid="column"] {
            flex: 0 0 50% !important;
            max-width: 50% !important;
        }
    }
    
    /* 通用移动端优化 */
    @media (max-width: 1024px) {
        /* 表格横向滚动提示 */
        .dataframe-container {
            overflow-x: auto;
        }
        
        /* 优化图表显示 */
        .js-plotly-plot {
            width: 100% !important;
        }
    }
    </style>
    """


def inject_responsive_css():
    """注入响应式 CSS 到页面"""
    st.markdown(get_responsive_css(), unsafe_allow_html=True)
