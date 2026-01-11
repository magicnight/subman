"""
MySub Manager - 全局配置文件
"""
from pathlib import Path

# 版本号
VERSION = "1.0.0"

# 项目根目录
BASE_DIR = Path(__file__).parent.parent

# 数据文件路径
DATA_DIR = BASE_DIR / "data"
SUBSCRIPTIONS_FILE = DATA_DIR / "subscriptions.csv"
SERVICE_FILE = DATA_DIR / "Service.csv"
SUBSCRIBE_TYPE_FILE = DATA_DIR / "Subscribe.csv"

# CSV 文件编码（支持 Excel 打开中文）
CSV_ENCODING = "utf-8-sig"

# 日期格式
DATE_FORMAT = "%Y-%m-%d"

# 预警天数（距离下次付费少于此天数时发出预警）
WARNING_DAYS = 7

# 页面配置
PAGE_TITLE = "MySub Manager"
PAGE_ICON = "📊"
LAYOUT = "wide"

# 主题颜色
PRIMARY_COLOR = "#FF4B4B"
BACKGROUND_COLOR = "#FFFFFF"
SECONDARY_BACKGROUND_COLOR = "#F0F2F6"

# KPI 卡片样式
KPI_CARD_STYLE = """
<style>
.metric-card {
    background-color: #f0f2f6;
    padding: 20px;
    border-radius: 10px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}
.metric-value {
    font-size: 2.5em;
    font-weight: bold;
    color: #FF4B4B;
}
.metric-label {
    font-size: 1em;
    color: #666;
}
</style>
"""

# 数据验证规则
REQUIRED_COLUMNS = [
    "名称",
    "服务性质",
    "订阅类型",
    "金额",
    "货币",
    "下次付费时间",
    "自动续费"
]

# 默认币种（泰铢）
DEFAULT_CURRENCY = "THB"
CURRENCY_SYMBOL = "฿"

# Streamlit 配置
STREAMLIT_CONFIG = {
    "page_title": PAGE_TITLE,
    "page_icon": PAGE_ICON,
    "layout": LAYOUT,
    "initial_sidebar_state": "expanded",
}
