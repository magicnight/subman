"""
通知提醒模块 - 订阅到期邮件/消息提醒
"""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
from typing import Optional
import pandas as pd
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()


def get_upcoming_subscriptions(df: pd.DataFrame, days: int = 7) -> pd.DataFrame:
    """
    获取即将到期的订阅
    
    Args:
        df: 订阅数据框
        days: 提前预警天数
        
    Returns:
        pd.DataFrame: 即将到期的订阅
    """
    if df.empty:
        return pd.DataFrame()
    
    # 筛选即将到期且自动续费的订阅
    upcoming = df[
        (df['剩余天数'] >= 0) & 
        (df['剩余天数'] <= days) &
        (df['自动续费'] == True)
    ].copy()
    
    return upcoming.sort_values('剩余天数')


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
    
    lines = [
        "🔔 MySub Manager 到期提醒",
        "=" * 40,
        f"您有 {len(subscriptions)} 个订阅即将自动续费：",
        ""
    ]
    
    total_amount = 0
    for _, row in subscriptions.iterrows():
        days_text = f"{row['剩余天数']} 天后" if row['剩余天数'] > 0 else "今天"
        lines.append(f"📌 {row['名称']} ({row['服务性质']})")
        lines.append(f"   💰 金额: {currency_symbol}{row['金额']:.2f}")
        lines.append(f"   ⏰ 到期: {days_text}")
        lines.append("")
        total_amount += row['金额']
    
    lines.append("=" * 40)
    lines.append(f"💸 总计: {currency_symbol}{total_amount:.2f}")
    lines.append("")
    lines.append("如需取消自动续费，请及时处理。")
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
    
    html = f"""
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; }}
            .header {{ background-color: #FF4B4B; color: white; padding: 20px; text-align: center; }}
            .content {{ padding: 20px; }}
            .subscription {{ background-color: #f5f5f5; padding: 15px; margin: 10px 0; border-radius: 8px; }}
            .amount {{ color: #FF4B4B; font-weight: bold; }}
            .footer {{ background-color: #333; color: white; padding: 15px; text-align: center; font-size: 12px; }}
            table {{ width: 100%; border-collapse: collapse; }}
            th, td {{ padding: 10px; text-align: left; border-bottom: 1px solid #ddd; }}
            th {{ background-color: #FF4B4B; color: white; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>🔔 MySub Manager 到期提醒</h1>
        </div>
        <div class="content">
            <p>您有 <strong>{len(subscriptions)}</strong> 个订阅即将自动续费：</p>
            <table>
                <tr>
                    <th>服务名称</th>
                    <th>类型</th>
                    <th>金额</th>
                    <th>剩余天数</th>
                </tr>
    """
    
    total_amount = 0
    for _, row in subscriptions.iterrows():
        html += f"""
                <tr>
                    <td>{row['名称']}</td>
                    <td>{row['服务性质']}</td>
                    <td class="amount">{currency_symbol}{row['金额']:.2f}</td>
                    <td>{row['剩余天数']} 天</td>
                </tr>
        """
        total_amount += row['金额']
    
    html += f"""
            </table>
            <p style="font-size: 18px; margin-top: 20px;">
                💸 <strong>总计: {currency_symbol}{total_amount:.2f}</strong>
            </p>
            <p style="color: #666;">如需取消自动续费，请及时处理。</p>
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


def check_and_remind(df: pd.DataFrame, days: int = 7, currency_symbol: str = '฿') -> tuple[bool, str]:
    """
    检查并发送提醒（主入口函数）
    
    Args:
        df: 订阅数据框
        days: 提前预警天数
        currency_symbol: 货币符号
        
    Returns:
        tuple[bool, str]: (是否成功, 消息)
    """
    upcoming = get_upcoming_subscriptions(df, days)
    
    if upcoming.empty:
        return True, "没有即将到期的订阅需要提醒"
    
    return send_email_reminder(upcoming, currency_symbol=currency_symbol)
