#!/usr/bin/env python
"""
MySub Manager - 订阅到期提醒脚本

独立运行的提醒脚本，可通过定时任务（cron/Task Scheduler）调用。

功能:
- 3 天内到期的订阅自动发送提醒
- 每个订阅每天最多发送 1 封提醒
- 使用 --force 忽略每日限制

使用方法:
    python remind.py              # 发送 3 天内到期提醒
    python remind.py --days 7     # 发送 7 天内到期提醒
    python remind.py --dry-run    # 仅显示提醒内容，不发送邮件
    python remind.py --force      # 忽略每日限制，强制发送
"""
import sys
import argparse
from pathlib import Path

# 添加项目根目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.config import CURRENCY_SYMBOL
from src.utils.notifications import (
    get_upcoming_subscriptions,
    format_reminder_message,
    check_and_remind,
    DEFAULT_WARNING_DAYS
)


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description='MySub Manager 订阅到期提醒',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
    python remind.py              # 发送 3 天内到期提醒
    python remind.py --days 7     # 发送 7 天内到期提醒  
    python remind.py --dry-run    # 仅显示提醒内容，不发送邮件
    python remind.py --force      # 忽略每日限制，强制发送
    python remind.py --email user@example.com  # 发送到指定邮箱
        """
    )
    
    parser.add_argument(
        '--days', '-d',
        type=int,
        default=DEFAULT_WARNING_DAYS,
        help=f'提前预警天数（默认: {DEFAULT_WARNING_DAYS}）'
    )
    
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='仅显示提醒内容，不发送邮件也不记录日志'
    )
    
    parser.add_argument(
        '--force', '-f',
        action='store_true',
        help='忽略每日发送限制，强制发送'
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
        import pandas as pd
        from src.config import SUBSCRIPTIONS_FILE, CSV_ENCODING
        from src.utils.data_loader import apply_auto_renewals, save_subscriptions_core

        df = pd.read_csv(SUBSCRIPTIONS_FILE, encoding=CSV_ENCODING)
        df['下次付费时间'] = pd.to_datetime(df['下次付费时间'])
        df['金额'] = pd.to_numeric(df['金额'], errors='coerce')
        df['自动续费'] = df['自动续费'].map({'TRUE': True, 'FALSE': False, True: True, False: False})
        df['剩余天数'] = (df['下次付费时间'] - pd.Timestamp.now()).dt.days

        # 对已过期且自动续费的订阅，按周期推进「下次付费时间」并写回
        df, changed = apply_auto_renewals(df)
        if changed:
            df['剩余天数'] = (df['下次付费时间'] - pd.Timestamp.now()).dt.days
            try:
                save_subscriptions_core(df)
                print("   🔄 已对到期的自动续费订阅更新下次付费时间并写回")
            except Exception as e:
                print(f"   ⚠️ 自动续期后保存失败: {e}")

        print(f"   ✅ 已加载 {len(df)} 条订阅记录")
    except Exception as e:
        print(f"   ❌ 加载失败: {e}")
        return 1

    print()

    # 获取即将到期的订阅（仅用于显示）
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
    
    # 使用新的 check_and_remind API
    print("=" * 50)
    
    if args.dry_run:
        print("📧 [DRY RUN] 检查发送状态...")
        success, msg, skipped = check_and_remind(
            df,
            days=args.days,
            currency_symbol=CURRENCY_SYMBOL,
            force=args.force,
            dry_run=True
        )
        print(f"   ℹ️ {msg}")
        if skipped:
            print(f"   ⏭️ 今日已发送（跳过）: {', '.join(skipped)}")
        print("   📧 未发送邮件，未记录日志")
    else:
        mode_text = "[强制模式]" if args.force else ""
        print(f"📧 发送邮件提醒... {mode_text}")
        
        success, msg, skipped = check_and_remind(
            df,
            days=args.days,
            currency_symbol=CURRENCY_SYMBOL,
            force=args.force,
            dry_run=False
        )
        
        if skipped:
            print(f"   ⏭️ 今日已发送（跳过）: {', '.join(skipped)}")
        
        if success:
            print(f"   ✅ {msg}")
        else:
            print(f"   ❌ {msg}")
            return 1
    
    print("=" * 50)
    return 0


if __name__ == "__main__":
    sys.exit(main())

