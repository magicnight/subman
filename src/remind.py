#!/usr/bin/env python
"""
MySub Manager - 订阅到期提醒脚本

独立运行的提醒脚本，可通过定时任务（cron/Task Scheduler）调用。

使用方法:
    python remind.py              # 发送 7 天内到期提醒
    python remind.py --days 14    # 发送 14 天内到期提醒
    python remind.py --dry-run    # 仅显示提醒内容，不发送邮件
"""
import sys
import argparse
from pathlib import Path

# 添加项目根目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.config import CURRENCY_SYMBOL
from src.utils.data_loader import load_subscriptions
from src.utils.notifications import (
    get_upcoming_subscriptions,
    format_reminder_message,
    send_email_reminder,
    check_and_remind
)


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description='MySub Manager 订阅到期提醒',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
    python remind.py              # 发送 7 天内到期提醒
    python remind.py --days 14    # 发送 14 天内到期提醒  
    python remind.py --dry-run    # 仅显示提醒内容，不发送邮件
    python remind.py --email user@example.com  # 发送到指定邮箱
        """
    )
    
    parser.add_argument(
        '--days', '-d',
        type=int,
        default=7,
        help='提前预警天数（默认: 7）'
    )
    
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='仅显示提醒内容，不发送邮件'
    )
    
    parser.add_argument(
        '--email', '-e',
        type=str,
        default=None,
        help='指定收件人邮箱（覆盖 .env 中的设置）'
    )
    
    args = parser.parse_args()
    
    print("=" * 50)
    print("📊 MySub Manager - 订阅到期提醒")
    print("=" * 50)
    print()
    
    # 加载订阅数据
    print("📂 加载订阅数据...")
    try:
        # 需要在非 Streamlit 环境下特殊处理
        import pandas as pd
        from src.config import SUBSCRIPTIONS_FILE, CSV_ENCODING, REQUIRED_COLUMNS
        
        df = pd.read_csv(SUBSCRIPTIONS_FILE, encoding=CSV_ENCODING)
        df['下次付费时间'] = pd.to_datetime(df['下次付费时间'])
        df['金额'] = pd.to_numeric(df['金额'], errors='coerce')
        df['自动续费'] = df['自动续费'].map({'TRUE': True, 'FALSE': False, True: True, False: False})
        df['剩余天数'] = (df['下次付费时间'] - pd.Timestamp.now()).dt.days
        
        print(f"   ✅ 已加载 {len(df)} 条订阅记录")
    except Exception as e:
        print(f"   ❌ 加载失败: {e}")
        return 1
    
    print()
    
    # 获取即将到期的订阅
    print(f"🔍 检查 {args.days} 天内到期的订阅...")
    upcoming = get_upcoming_subscriptions(df, args.days)
    
    if upcoming.empty:
        print("   ✅ 没有即将到期的自动续费订阅")
        print()
        print("=" * 50)
        return 0
    
    print(f"   ⚠️ 发现 {len(upcoming)} 个即将到期的订阅")
    print()
    
    # 显示提醒内容
    message = format_reminder_message(upcoming, CURRENCY_SYMBOL)
    print(message)
    print()
    
    # 发送邮件
    if args.dry_run:
        print("=" * 50)
        print("📧 [DRY RUN] 未发送邮件")
        print("=" * 50)
    else:
        print("=" * 50)
        print("📧 发送邮件提醒...")
        success, msg = send_email_reminder(
            upcoming,
            recipient_email=args.email,
            currency_symbol=CURRENCY_SYMBOL
        )
        
        if success:
            print(f"   ✅ {msg}")
        else:
            print(f"   ❌ {msg}")
            return 1
        
        print("=" * 50)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
