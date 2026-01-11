"""
汇率换算模块 - 使用泰国央行 (BOT) API 获取实时汇率
支持 CSV 文件缓存和状态显示
"""
import http.client
import json
import os
from datetime import datetime, timedelta
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path
from typing import Optional
import pandas as pd
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# BOT API 配置（从环境变量读取）
BOT_API_HOST = "gateway.api.bot.or.th"
BOT_API_PATH = "/Stat-ExchangeRate/v2/DAILY_AVG_EXG_RATE/"
BOT_API_TOKEN = os.getenv('BOT_API_TOKEN', '')

# 数据目录
DATA_DIR = Path(__file__).parent.parent.parent / "data"
EXCHANGE_RATE_FILE = DATA_DIR / "exchangerate.csv"
CSV_ENCODING = "utf-8-sig"

# 缓存有效期（秒）
CACHE_TTL_SECONDS = 3600  # 1 小时

# 支持的货币类型（BOT API 支持的货币）
SUPPORTED_CURRENCIES = [
    'THB', 'USD', 'EUR', 'GBP', 'JPY', 'CNY', 'HKD', 'SGD',
    'AUD', 'NZD', 'CHF', 'CAD', 'MYR', 'KRW', 'INR', 'TWD',
    'SAR', 'AED', 'DKK', 'SEK', 'NOK'
]

# 货币符号映射
CURRENCY_SYMBOLS = {
    'THB': '฿', 'USD': '$', 'EUR': '€', 'GBP': '£', 'JPY': '¥',
    'CNY': '¥', 'HKD': 'HK$', 'SGD': 'S$', 'AUD': 'A$', 'NZD': 'NZ$',
    'CHF': 'CHF', 'CAD': 'C$', 'MYR': 'RM', 'KRW': '₩', 'INR': '₹',
    'TWD': 'NT$', 'SAR': '﷼', 'AED': 'د.إ', 'DKK': 'kr', 'SEK': 'kr', 'NOK': 'kr'
}

# 备用静态汇率（API 失败时使用）
FALLBACK_RATES = {
    'THB': Decimal('1.0'),
    'USD': Decimal('35.50'),
    'EUR': Decimal('38.80'),
    'GBP': Decimal('45.20'),
    'JPY': Decimal('0.24'),
    'CNY': Decimal('4.95'),
    'HKD': Decimal('4.55'),
    'SGD': Decimal('26.50'),
    'AUD': Decimal('23.50'),
    'NZD': Decimal('21.50'),
    'CHF': Decimal('40.00'),
    'CAD': Decimal('26.00'),
    'MYR': Decimal('7.80'),
    'KRW': Decimal('0.027'),
    'INR': Decimal('0.43'),
}

# 汇率状态信息
_rate_status = {
    'status': 'unknown',  # 'success', 'updating', 'error', 'cached', 'fallback'
    'message': '',
    'last_updated': None,
    'source': 'unknown'
}


def load_rates_from_csv() -> tuple[dict[str, Decimal], Optional[datetime]]:
    """
    从 CSV 文件加载汇率数据
    
    Returns:
        tuple: (汇率字典, 最后更新时间)
    """
    if not EXCHANGE_RATE_FILE.exists():
        return {}, None
    
    try:
        df = pd.read_csv(EXCHANGE_RATE_FILE, encoding=CSV_ENCODING)
        
        if df.empty or 'currency' not in df.columns or 'rate' not in df.columns:
            return {}, None
        
        # 获取最后更新时间
        last_updated = None
        if 'updated_at' in df.columns and len(df) > 0:
            last_updated = pd.to_datetime(df['updated_at'].iloc[0])
        
        # 构建汇率字典
        rates = {'THB': Decimal('1.0')}
        for _, row in df.iterrows():
            try:
                rates[row['currency']] = Decimal(str(row['rate']))
            except:
                pass
        
        return rates, last_updated
        
    except Exception as e:
        print(f"读取汇率 CSV 失败: {e}")
        return {}, None


def save_rates_to_csv(rates: dict[str, Decimal]) -> bool:
    """
    保存汇率数据到 CSV 文件
    
    Args:
        rates: 汇率字典
        
    Returns:
        bool: 保存是否成功
    """
    try:
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        data = []
        for currency, rate in rates.items():
            if currency != 'THB':  # THB 始终为 1，不需要存储
                data.append({
                    'currency': currency,
                    'rate': float(rate),
                    'updated_at': now
                })
        
        df = pd.DataFrame(data)
        df.to_csv(EXCHANGE_RATE_FILE, index=False, encoding=CSV_ENCODING)
        return True
        
    except Exception as e:
        print(f"保存汇率 CSV 失败: {e}")
        return False


def fetch_exchange_rates_from_bot(date: Optional[str] = None) -> dict[str, Decimal]:
    """
    从泰国央行 API 获取汇率数据
    
    Args:
        date: 日期字符串 (YYYY-MM-DD)，如果为 None 则自动查找最近有效的工作日
        
    Returns:
        dict: 货币代码 -> THB 汇率的映射
    """
    global _rate_status
    
    if not BOT_API_TOKEN:
        _rate_status['status'] = 'error'
        _rate_status['message'] = 'BOT_API_TOKEN 未配置，请在 .env 文件中设置'
        return {}
    
    _rate_status['status'] = 'updating'
    _rate_status['message'] = '正在从泰国央行获取汇率...'
    
    # 如果没有指定日期，尝试最近 7 天（避免周末/假期无数据）
    dates_to_try = []
    if date is None:
        for days_ago in range(1, 8):
            target = datetime.now() - timedelta(days=days_ago)
            dates_to_try.append(target.strftime('%Y-%m-%d'))
    else:
        dates_to_try = [date]
    
    try:
        conn = http.client.HTTPSConnection(BOT_API_HOST, timeout=10)
        
        headers = {
            'Accept': 'application/json',
            'Authorization': BOT_API_TOKEN
        }
        
        # 遍历日期列表，直到找到有效数据
        for try_date in dates_to_try:
            query = f"?start_period={try_date}&end_period={try_date}"
            conn.request("GET", f"{BOT_API_PATH}{query}", headers=headers)
            res = conn.getresponse()
            
            if res.status != 200:
                _rate_status['status'] = 'error'
                _rate_status['message'] = f'API 返回状态码: {res.status}'
                return {}
            
            data = json.loads(res.read().decode('utf-8'))
            
            # 解析响应
            rates = {'THB': Decimal('1.0')}
            
            result = data.get('result', {})
            data_detail = result.get('data', {}).get('data_detail', [])
            
            if isinstance(data_detail, list):
                for item in data_detail:
                    currency_id = item.get('currency_id', '')
                    mid_rate = item.get('mid_rate', '')
                    
                    if currency_id and mid_rate:
                        try:
                            rates[currency_id] = Decimal(mid_rate)
                        except:
                            pass
            
            # 如果获取到有效汇率，更新状态并返回
            if len(rates) > 1:
                _rate_status['status'] = 'success'
                _rate_status['message'] = f'汇率更新成功（{try_date}），获取到 {len(rates)} 种货币'
                _rate_status['last_updated'] = datetime.now()
                _rate_status['source'] = 'Bank of Thailand API'
                
                # 保存到 CSV
                save_rates_to_csv(rates)
                conn.close()
                return rates
        
        # 遍历所有日期都没有有效数据
        conn.close()
        _rate_status['status'] = 'error'
        _rate_status['message'] = '未能获取有效汇率数据（可能为假期）'
        return {'THB': Decimal('1.0')}
        
    except Exception as e:
        _rate_status['status'] = 'error'
        _rate_status['message'] = f'API 调用失败: {str(e)}'
        return {}


def get_exchange_rates(force_refresh: bool = False) -> dict[str, Decimal]:
    """
    获取汇率数据（优先使用 CSV 缓存）
    
    Args:
        force_refresh: 是否强制从 API 刷新
        
    Returns:
        dict: 货币代码 -> THB 汇率的映射
    """
    global _rate_status
    
    # 如果不强制刷新，先尝试从 CSV 加载
    if not force_refresh:
        cached_rates, last_updated = load_rates_from_csv()
        
        if cached_rates and last_updated:
            age_seconds = (datetime.now() - last_updated).total_seconds()
            
            if age_seconds < CACHE_TTL_SECONDS:
                _rate_status['status'] = 'cached'
                _rate_status['message'] = f'使用缓存汇率（{int(age_seconds / 60)} 分钟前更新）'
                _rate_status['last_updated'] = last_updated
                _rate_status['source'] = 'CSV 缓存'
                return cached_rates
    
    # 从 API 获取汇率
    rates = fetch_exchange_rates_from_bot()
    
    if rates:
        return rates
    
    # API 失败，尝试使用过期的 CSV 缓存
    cached_rates, last_updated = load_rates_from_csv()
    if cached_rates:
        _rate_status['status'] = 'cached'
        _rate_status['message'] = 'API 失败，使用历史缓存汇率'
        _rate_status['last_updated'] = last_updated
        _rate_status['source'] = 'CSV 缓存（过期）'
        return cached_rates
    
    # 最后使用备用汇率
    _rate_status['status'] = 'fallback'
    _rate_status['message'] = 'API 失败，使用备用静态汇率'
    _rate_status['source'] = '备用静态汇率'
    return FALLBACK_RATES.copy()


def get_rate_status() -> dict:
    """
    获取汇率更新状态
    
    Returns:
        dict: 状态信息
    """
    return _rate_status.copy()


def convert_to_thb(amount: float, currency: str) -> float:
    """
    将指定货币金额转换为泰铢
    """
    if currency == 'THB':
        return amount
    
    rates = get_exchange_rates()
    rate = rates.get(currency, FALLBACK_RATES.get(currency, Decimal('1.0')))
    
    decimal_amount = Decimal(str(amount))
    thb_amount = decimal_amount * rate
    
    return float(thb_amount.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP))


def convert_from_thb(thb_amount: float, target_currency: str) -> float:
    """
    将泰铢金额转换为指定货币
    """
    if target_currency == 'THB':
        return thb_amount
    
    rates = get_exchange_rates()
    rate = rates.get(target_currency, FALLBACK_RATES.get(target_currency, Decimal('1.0')))
    
    if rate == 0:
        return 0.0
    
    decimal_amount = Decimal(str(thb_amount))
    converted_amount = decimal_amount / rate
    
    return float(converted_amount.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP))


def get_currency_symbol(currency: str) -> str:
    """获取货币符号"""
    return CURRENCY_SYMBOLS.get(currency, currency)


def format_currency(amount: float, currency: str) -> str:
    """格式化货币显示"""
    symbol = get_currency_symbol(currency)
    return f"{symbol}{amount:,.2f}"


def get_exchange_rate(from_currency: str, to_currency: str = 'THB') -> Optional[float]:
    """获取汇率"""
    rates = get_exchange_rates()
    
    if from_currency not in rates or to_currency not in rates:
        return None
    
    from_rate = rates[from_currency]
    to_rate = rates[to_currency]
    
    if to_rate == 0:
        return None
    
    cross_rate = from_rate / to_rate
    return float(cross_rate.quantize(Decimal('0.0001'), rounding=ROUND_HALF_UP))


def get_all_rates() -> dict[str, float]:
    """获取所有可用货币的汇率"""
    rates = get_exchange_rates()
    return {k: float(v) for k, v in rates.items()}


def get_rate_info() -> dict:
    """获取汇率信息（兼容旧接口）"""
    status = get_rate_status()
    return {
        'source': status.get('source', 'Unknown'),
        'api': 'Daily Average Exchange Rate',
        'last_updated': status.get('last_updated'),
        'status': status.get('status'),
        'message': status.get('message')
    }


def render_rate_status():
    """
    渲染汇率状态组件（在 Streamlit 页面中使用）
    """
    try:
        import streamlit as st
        
        # 确保汇率已加载（这会触发状态更新）
        get_exchange_rates()
        
        status = get_rate_status()
        
        # 状态图标
        status_icons = {
            'success': '✅',
            'cached': '📦',
            'updating': '🔄',
            'error': '❌',
            'fallback': '⚠️',
            'unknown': '❓'
        }
        
        icon = status_icons.get(status['status'], '❓')
        message = status.get('message', '未知状态')
        
        # 最后更新时间
        last_updated = status.get('last_updated')
        if last_updated:
            time_str = last_updated.strftime('%Y-%m-%d %H:%M')
            st.caption(f"{icon} {message} | 🕐 {time_str}")
        else:
            st.caption(f"{icon} {message}")
            
    except ImportError:
        pass

