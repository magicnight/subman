"""
通知提醒模块 - 订阅到期邮件/消息提醒

功能:
- 3 天内到期的订阅自动发送提醒
- 每个订阅每天最多发送 1 封提醒
- 持久化保存发送状态到 CSV
- 订阅过期后自动停止提醒
"""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
from typing import Optional
from pathlib import Path
import pandas as pd
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 数据目录
DATA_DIR = Path(__file__).parent.parent.parent / "data"
NOTIFICATION_LOG_FILE = DATA_DIR / "notification_log.csv"
CSV_ENCODING = "utf-8-sig"

# 日志列定义
LOG_COLUMNS = ['subscription_name', 'sent_date', 'days_remaining', 'email_sent']

# 默认预警天数
DEFAULT_WARNING_DAYS = 3


def load_notification_log() -> pd.DataFrame:
    """
    加载通知发送日志
    
    Returns:
        pd.DataFrame: 发送日志数据框
    """
    if not NOTIFICATION_LOG_FILE.exists():
        return pd.DataFrame(columns=LOG_COLUMNS)
    
    try:
        df = pd.read_csv(NOTIFICATION_LOG_FILE, encoding=CSV_ENCODING)
        df['sent_date'] = pd.to_datetime(df['sent_date']).dt.date
        return df
    except Exception as e:
        print(f"加载通知日志失败: {e}")
        return pd.DataFrame(columns=LOG_COLUMNS)


def save_notification_log(df: pd.DataFrame) -> bool:
    """
    保存通知发送日志
    
    Args:
        df: 发送日志数据框
        
    Returns:
        bool: 保存是否成功
    """
    try:
        save_df = df.copy()
        save_df['sent_date'] = pd.to_datetime(save_df['sent_date']).dt.strftime('%Y-%m-%d')
        save_df.to_csv(NOTIFICATION_LOG_FILE, index=False, encoding=CSV_ENCODING)
        return True
    except Exception as e:
        print(f"保存通知日志失败: {e}")
        return False


def should_send_reminder(subscription_name: str, log_df: pd.DataFrame) -> bool:
    """
    检查今天是否应该发送提醒
    
    Args:
        subscription_name: 订阅名称
        log_df: 发送日志数据框
        
    Returns:
        bool: True 表示应该发送，False 表示今日已发送
    """
    today = datetime.now().date()
    
    if log_df.empty:
        return True
    
    # 检查今天是否已经发送过
    today_sent = log_df[
        (log_df['subscription_name'] == subscription_name) &
        (log_df['sent_date'] == today) &
        (log_df['email_sent'] == True)
    ]
    
    return today_sent.empty


def record_sent_notification(
    log_df: pd.DataFrame,
    subscription_name: str,
    days_remaining: int,
    email_sent: bool = True
) -> pd.DataFrame:
    """
    记录发送的通知
    
    Args:
        log_df: 当前日志数据框
        subscription_name: 订阅名称
        days_remaining: 剩余天数
        email_sent: 是否成功发送
        
    Returns:
        pd.DataFrame: 更新后的日志数据框
    """
    new_record = {
        'subscription_name': subscription_name,
        'sent_date': datetime.now().date(),
        'days_remaining': days_remaining,
        'email_sent': email_sent
    }
    
    new_row = pd.DataFrame([new_record])
    return pd.concat([log_df, new_row], ignore_index=True)


def cleanup_old_logs(log_df: pd.DataFrame, days_to_keep: int = 30) -> pd.DataFrame:
    """
    清理过期的日志记录
    
    Args:
        log_df: 日志数据框
        days_to_keep: 保留最近多少天的记录
        
    Returns:
        pd.DataFrame: 清理后的日志数据框
    """
    if log_df.empty:
        return log_df
    
    cutoff_date = datetime.now().date() - timedelta(days=days_to_keep)
    return log_df[log_df['sent_date'] >= cutoff_date].copy()


def get_upcoming_subscriptions(df: pd.DataFrame, days: int = DEFAULT_WARNING_DAYS) -> pd.DataFrame:
    """
    获取即将到期的订阅（包括自动续费和手动续费）
    
    Args:
        df: 订阅数据框
        days: 提前预警天数（默认 3 天）
        
    Returns:
        pd.DataFrame: 即将到期的订阅
    """
    if df.empty:
        return pd.DataFrame()
    
    # 筛选即将到期的订阅（包括所有类型）
    upcoming = df[
        (df['剩余天数'] >= 0) & 
        (df['剩余天数'] <= days)
    ].copy()
    
    return upcoming.sort_values('剩余天数')


def filter_subscriptions_for_today(
    subscriptions: pd.DataFrame,
    force: bool = False
) -> tuple[pd.DataFrame, list[str]]:
    """
    过滤今天需要发送提醒的订阅
    
    Args:
        subscriptions: 即将到期的订阅数据框
        force: 是否强制发送（忽略每日限制）
        
    Returns:
        tuple: (需要发送的订阅, 跳过的订阅名称列表)
    """
    if force or subscriptions.empty:
        return subscriptions, []
    
    log_df = load_notification_log()
    to_send = []
    skipped = []
    
    for idx, row in subscriptions.iterrows():
        name = row['名称']
        if should_send_reminder(name, log_df):
            to_send.append(idx)
        else:
            skipped.append(name)
    
    return subscriptions.loc[to_send].copy() if to_send else pd.DataFrame(), skipped


def format_reminder_message(subscriptions: pd.DataFrame, currency_symbol: str = '฿') -> str:
    """
    格式化提醒消息内容
    
    Args:
        subscriptions: 即将到期的订阅数据框
        currency_symbol: 货币符号
        
    Returns:
        str: 格式化的消息内容
    """
    if subscriptions.empty:
        return "✅ 近期没有需要关注的订阅续费。"
    
    # 分类订阅
    auto_renew = subscriptions[subscriptions['自动续费'] == True]
    manual_renew = subscriptions[subscriptions['自动续费'] != True]
    
    lines = [
        "🔔 MySub Manager 到期提醒",
        "=" * 40,
        f"您有 {len(subscriptions)} 个订阅即将到期：",
        ""
    ]
    
    total_amount = 0
    
    # 自动续费订阅
    if not auto_renew.empty:
        lines.append("🔄 【自动续费】以下订阅将自动扣款：")
        lines.append("")
        for _, row in auto_renew.iterrows():
            days_text = f"{row['剩余天数']} 天后" if row['剩余天数'] > 0 else "今天"
            lines.append(f"📌 {row['名称']} ({row['服务性质']})")
            lines.append(f"   💰 金额: {currency_symbol}{row['金额']:.2f}")
            lines.append(f"   ⏰ 到期: {days_text}")
            lines.append("")
            total_amount += row['金额']
    
    # 手动续费订阅
    if not manual_renew.empty:
        lines.append("⚠️ 【需手动续期】以下订阅如不续期将过期：")
        lines.append("")
        for _, row in manual_renew.iterrows():
            days_text = f"{row['剩余天数']} 天后" if row['剩余天数'] > 0 else "今天"
            lines.append(f"📌 {row['名称']} ({row['服务性质']})")
            lines.append(f"   💰 金额: {currency_symbol}{row['金额']:.2f}")
            lines.append(f"   ⏰ 到期: {days_text}")
            lines.append("")
            total_amount += row['金额']
    
    lines.append("=" * 40)
    lines.append(f"💸 总计: {currency_symbol}{total_amount:.2f}")
    lines.append("")
    if not auto_renew.empty:
        lines.append("🔄 自动续费订阅如需取消，请及时处理。")
    if not manual_renew.empty:
        lines.append("⚠️ 手动续期订阅请记得续费，否则将失效。")
    lines.append(f"发送时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    
    return "\n".join(lines)


def format_html_reminder(subscriptions: pd.DataFrame, currency_symbol: str = '฿') -> str:
    """
    格式化 HTML 格式的提醒邮件
    
    Args:
        subscriptions: 即将到期的订阅数据框
        currency_symbol: 货币符号
        
    Returns:
        str: HTML 格式的邮件内容
    """
    if subscriptions.empty:
        return "<p>✅ 近期没有需要关注的订阅续费。</p>"
    
    # 分类订阅
    auto_renew = subscriptions[subscriptions['自动续费'] == True]
    manual_renew = subscriptions[subscriptions['自动续费'] != True]
    
    html = f"""
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; }}
            .header {{ background-color: #FF4B4B; color: white; padding: 20px; text-align: center; }}
            .content {{ padding: 20px; }}
            .section-title {{ background-color: #f0f0f0; padding: 10px; margin: 15px 0 10px 0; border-radius: 5px; }}
            .auto-renew {{ color: #FF4B4B; }}
            .manual-renew {{ color: #FFA500; }}
            .amount {{ color: #FF4B4B; font-weight: bold; }}
            .footer {{ background-color: #333; color: white; padding: 15px; text-align: center; font-size: 12px; }}
            table {{ width: 100%; border-collapse: collapse; margin-bottom: 20px; }}
            th, td {{ padding: 10px; text-align: left; border-bottom: 1px solid #ddd; }}
            th {{ background-color: #FF4B4B; color: white; }}
            .warning {{ background-color: #fff3cd; border: 1px solid #ffc107; padding: 10px; border-radius: 5px; margin: 10px 0; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>🔔 MySub Manager 到期提醒</h1>
        </div>
        <div class="content">
            <p>您有 <strong>{len(subscriptions)}</strong> 个订阅即将到期：</p>
    """
    
    total_amount = 0
    
    # 自动续费订阅表格
    if not auto_renew.empty:
        html += """
            <div class="section-title auto-renew">🔄 【自动续费】以下订阅将自动扣款：</div>
            <table>
                <tr>
                    <th>服务名称</th>
                    <th>类型</th>
                    <th>金额</th>
                    <th>剩余天数</th>
                </tr>
        """
        for _, row in auto_renew.iterrows():
            html += f"""
                <tr>
                    <td>{row['名称']}</td>
                    <td>{row['服务性质']}</td>
                    <td class="amount">{currency_symbol}{row['金额']:.2f}</td>
                    <td>{row['剩余天数']} 天</td>
                </tr>
            """
            total_amount += row['金额']
        html += "</table>"
    
    # 手动续费订阅表格
    if not manual_renew.empty:
        html += """
            <div class="section-title manual-renew">⚠️ 【需手动续期】以下订阅如不续期将过期：</div>
            <table>
                <tr>
                    <th>服务名称</th>
                    <th>类型</th>
                    <th>金额</th>
                    <th>剩余天数</th>
                </tr>
        """
        for _, row in manual_renew.iterrows():
            html += f"""
                <tr>
                    <td>{row['名称']}</td>
                    <td>{row['服务性质']}</td>
                    <td class="amount">{currency_symbol}{row['金额']:.2f}</td>
                    <td>{row['剩余天数']} 天</td>
                </tr>
            """
            total_amount += row['金额']
        html += "</table>"
    
    # 底部信息
    html += f"""
            <p style="font-size: 18px; margin-top: 20px;">
                💸 <strong>总计: {currency_symbol}{total_amount:.2f}</strong>
            </p>
    """
    
    if not auto_renew.empty:
        html += '<p style="color: #666;">🔄 自动续费订阅如需取消，请及时处理。</p>'
    if not manual_renew.empty:
        html += '<div class="warning">⚠️ 手动续期订阅请记得续费，否则将失效！</div>'
    
    html += f"""
        </div>
        <div class="footer">
            <p>MySub Manager - 让每一笔订阅都清晰可见</p>
            <p>发送时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}</p>
        </div>
    </body>
    </html>
    """
    
    return html


def send_email_reminder(
    subscriptions: pd.DataFrame,
    recipient_email: Optional[str] = None,
    currency_symbol: str = '฿'
) -> tuple[bool, str]:
    """
    发送邮件提醒
    
    Args:
        subscriptions: 即将到期的订阅数据框
        recipient_email: 收件人邮箱（可选，默认从环境变量读取）
        currency_symbol: 货币符号
        
    Returns:
        tuple[bool, str]: (是否成功, 消息)
    """
    # 读取邮件配置
    smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
    smtp_port = int(os.getenv('SMTP_PORT', '587'))
    smtp_username = os.getenv('SMTP_USERNAME', '')
    smtp_password = os.getenv('SMTP_PASSWORD', '')
    sender_email = os.getenv('SENDER_EMAIL', smtp_username)
    recipient = recipient_email or os.getenv('RECIPIENT_EMAIL', '')
    
    # 验证必要配置
    if not all([smtp_username, smtp_password, recipient]):
        return False, "邮件配置不完整，请检查 .env 文件中的 SMTP 设置"
    
    if subscriptions.empty:
        return True, "没有需要提醒的订阅"
    
    try:
        # 创建邮件
        msg = MIMEMultipart('alternative')
        msg['Subject'] = f'🔔 MySub Manager: {len(subscriptions)} 个订阅即将自动续费'
        msg['From'] = sender_email
        msg['To'] = recipient
        
        # 纯文本版本
        text_content = format_reminder_message(subscriptions, currency_symbol)
        msg.attach(MIMEText(text_content, 'plain', 'utf-8'))
        
        # HTML 版本
        html_content = format_html_reminder(subscriptions, currency_symbol)
        msg.attach(MIMEText(html_content, 'html', 'utf-8'))
        
        # 发送邮件
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(smtp_username, smtp_password)
            server.send_message(msg)
        
        return True, f"成功发送提醒邮件到 {recipient}"
        
    except smtplib.SMTPAuthenticationError:
        return False, "SMTP 认证失败，请检查用户名和密码"
    except smtplib.SMTPException as e:
        return False, f"SMTP 错误: {str(e)}"
    except Exception as e:
        return False, f"发送邮件失败: {str(e)}"


def check_and_remind(
    df: pd.DataFrame,
    days: int = DEFAULT_WARNING_DAYS,
    currency_symbol: str = '฿',
    force: bool = False,
    dry_run: bool = False
) -> tuple[bool, str, list[str]]:
    """
    检查并发送提醒（主入口函数）
    
    Args:
        df: 订阅数据框
        days: 提前预警天数（默认 3 天）
        currency_symbol: 货币符号
        force: 是否强制发送（忽略每日限制）
        dry_run: 仅预览，不发送邮件也不记录日志
        
    Returns:
        tuple[bool, str, list[str]]: (是否成功, 消息, 跳过的订阅列表)
    """
    # 获取即将到期的订阅
    upcoming = get_upcoming_subscriptions(df, days)
    
    if upcoming.empty:
        return True, "没有即将到期的订阅需要提醒", []
    
    # 过滤今天需要发送的订阅
    to_send, skipped = filter_subscriptions_for_today(upcoming, force)
    
    if to_send.empty:
        return True, f"所有 {len(upcoming)} 个订阅今日已发送过提醒", skipped
    
    # 如果是 dry run 模式，只返回信息不发送
    if dry_run:
        return True, f"[DRY RUN] 将发送 {len(to_send)} 个订阅的提醒", skipped
    
    # 发送邮件
    success, message = send_email_reminder(to_send, currency_symbol=currency_symbol)
    
    if success:
        # 记录发送状态
        log_df = load_notification_log()
        for _, row in to_send.iterrows():
            log_df = record_sent_notification(
                log_df,
                row['名称'],
                row['剩余天数'],
                email_sent=True
            )
        
        # 清理旧日志并保存
        log_df = cleanup_old_logs(log_df)
        save_notification_log(log_df)
    
    return success, message, skipped

