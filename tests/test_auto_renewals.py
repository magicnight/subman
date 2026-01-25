"""
测试自动续费逻辑：对已过期且勾选自动续费的订阅，按周期推进「下次付费时间」。
"""
import pandas as pd
import pytest

from src.utils.data_loader import apply_auto_renewals


def test_apply_auto_renewals_monthly_expired():
    """月付、已过期、自动续费：下次付费时间应加 1 个月"""
    now = pd.Timestamp.now().normalize()
    past = now - pd.DateOffset(months=1)
    df = pd.DataFrame([{
        '下次付费时间': past,
        '剩余天数': -30,
        '自动续费': True,
        '订阅类型': '月付',
    }])
    out, changed = apply_auto_renewals(df)
    assert changed is True
    next_dt = pd.Timestamp(out.at[0, '下次付费时间']).normalize()
    assert next_dt >= now
    assert (next_dt - past).days >= 28  # 约 1 个月


def test_apply_auto_renewals_yearly_expired():
    """年付、已过期、自动续费：下次付费时间应加 1 年"""
    now = pd.Timestamp.now().normalize()
    past = now - pd.DateOffset(days=400)
    df = pd.DataFrame([{
        '下次付费时间': past,
        '剩余天数': -400,
        '自动续费': True,
        '订阅类型': '年付',
    }])
    out, changed = apply_auto_renewals(df)
    assert changed is True
    next_dt = pd.Timestamp(out.at[0, '下次付费时间']).normalize()
    assert next_dt >= now
    assert (next_dt - past).days >= 365


def test_apply_auto_renewals_not_auto_renew_unchanged():
    """未勾选自动续费：即使过期也不推进"""
    now = pd.Timestamp.now().normalize()
    past = now - pd.DateOffset(days=10)
    df = pd.DataFrame([{
        '下次付费时间': past,
        '剩余天数': -10,
        '自动续费': False,
        '订阅类型': '月付',
    }])
    out, changed = apply_auto_renewals(df)
    assert changed is False
    assert pd.Timestamp(out.at[0, '下次付费时间']).normalize() == past


def test_apply_auto_renewals_lifetime_unchanged():
    """终身：即使过期且自动续费也不推进"""
    now = pd.Timestamp.now().normalize()
    past = now - pd.DateOffset(days=10)
    df = pd.DataFrame([{
        '下次付费时间': past,
        '剩余天数': -10,
        '自动续费': True,
        '订阅类型': '终身',
    }])
    out, changed = apply_auto_renewals(df)
    assert changed is False
    assert pd.Timestamp(out.at[0, '下次付费时间']).normalize() == past


def test_apply_auto_renewals_not_expired_unchanged():
    """未过期：不推进"""
    now = pd.Timestamp.now().normalize()
    future = now + pd.DateOffset(days=10)
    df = pd.DataFrame([{
        '下次付费时间': future,
        '剩余天数': 10,
        '自动续费': True,
        '订阅类型': '月付',
    }])
    out, changed = apply_auto_renewals(df)
    assert changed is False
    assert pd.Timestamp(out.at[0, '下次付费时间']).normalize() == future


def test_apply_auto_renewals_multiple_periods_until_future():
    """过期多个月付周期：应一直加到超过今天"""
    now = pd.Timestamp.now().normalize()
    past = now - pd.DateOffset(months=5)
    df = pd.DataFrame([{
        '下次付费时间': past,
        '剩余天数': -150,
        '自动续费': True,
        '订阅类型': '月付',
    }])
    out, changed = apply_auto_renewals(df)
    assert changed is True
    next_dt = pd.Timestamp(out.at[0, '下次付费时间']).normalize()
    assert next_dt >= now
