#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
计息天数验证脚本
用于核查天津驹丰供应链管理有限公司债权的计息天数计算
"""

from datetime import datetime, timedelta

def calculate_days_between(start_date_str, end_date_str, method="exclude_both_ends"):
    """
    计算两个日期之间的天数

    参数:
        start_date_str: 起始日期，格式 "YYYY-MM-DD"
        end_date_str: 结束日期，格式 "YYYY-MM-DD"
        method: 计算方法
            - "exclude_both_ends": 不包含起止日（首尾都不算）
            - "exclude_start": 不包含起始日，包含结束日
            - "exclude_end": 包含起始日，不包含结束日（常用于利息计算）
            - "include_both_ends": 包含起止日（首尾都算）

    返回:
        天数（整数）
    """
    start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
    end_date = datetime.strptime(end_date_str, "%Y-%m-%d")

    # 基础天数差（自然天数差，不含起始日）
    delta = (end_date - start_date).days

    if method == "exclude_both_ends":
        # 不包含起止日：delta - 1
        return delta - 1
    elif method == "exclude_start":
        # 不包含起始日，包含结束日：delta
        return delta
    elif method == "exclude_end":
        # 包含起始日，不包含结束日：delta
        return delta
    elif method == "include_both_ends":
        # 包含起止日：delta + 1
        return delta + 1
    else:
        raise ValueError(f"未知的计算方法: {method}")


def main():
    # 计息期间
    start_date = "2022-02-15"  # 调解书生效日
    end_date = "2023-05-11"    # 破产受理日前一日

    print("=" * 70)
    print("天津驹丰供应链管理有限公司 - 计息天数核查")
    print("=" * 70)
    print(f"\n起始日期（调解书生效日）: {start_date}")
    print(f"结束日期（破产受理日前一日）: {end_date}")
    print("\n" + "-" * 70)

    # 计算各种方法下的天数
    methods = {
        "不包含起止日": "exclude_both_ends",
        "不包含起始日，包含结束日": "exclude_start",
        "包含起始日，不包含结束日": "exclude_end",
        "包含起止日": "include_both_ends"
    }

    results = {}
    for desc, method in methods.items():
        days = calculate_days_between(start_date, end_date, method)
        results[desc] = days
        print(f"{desc:25s}: {days:4d} 天")

    print("-" * 70)

    # Python timedelta 基础计算（自然天数差）
    start = datetime.strptime(start_date, "%Y-%m-%d")
    end = datetime.strptime(end_date, "%Y-%m-%d")
    natural_days = (end - start).days
    print(f"\nPython timedelta 自然天数差: {natural_days} 天")
    print("（注：timedelta.days 返回的是不含起始日的天数）")

    print("\n" + "=" * 70)
    print("对比分析")
    print("=" * 70)
    print(f"债权人申报计算:     450 天")
    print(f"Agent系统计算:      451 天")
    print(f"律师人工审阅:       452 天")
    print(f"本脚本验证结果:     {natural_days} 天 (timedelta.days)")

    print("\n" + "=" * 70)
    print("结论分析")
    print("=" * 70)

    if natural_days == 451:
        print("\n✓ Agent系统计算的451天是正确的（使用timedelta.days标准方法）")
        print("\n差异原因分析:")
        print("  • 债权人的450天: 可能手工计算错误，或使用了\"不包含起止日\"方法")
        print("  • 律师的452天: 可能使用了\"包含起止日\"方法（首尾都算）")
        print("\n建议:")
        print("  根据《民法典》第200条及破产法实务惯例，期间以日计算的，")
        print("  开始之日不算入（即从第二日开始计算），因此应采用451天。")

    # 逐月验证
    print("\n" + "=" * 70)
    print("逐月天数验证（与债权人申报表对比）")
    print("=" * 70)

    months_2022 = [
        ("2月", "2022-02-15", "2022-02-28"),
        ("3月", "2022-03-01", "2022-03-31"),
        ("4月", "2022-04-01", "2022-04-30"),
        ("5月", "2022-05-01", "2022-05-31"),
        ("6月", "2022-06-01", "2022-06-30"),
        ("7月", "2022-07-01", "2022-07-31"),
        ("8月", "2022-08-01", "2022-08-31"),
        ("9月", "2022-09-01", "2022-09-30"),
        ("10月", "2022-10-01", "2022-10-31"),
        ("11月", "2022-11-01", "2022-11-30"),
        ("12月", "2022-12-01", "2022-12-31"),
    ]

    months_2023 = [
        ("1月", "2023-01-01", "2023-01-31"),
        ("2月", "2023-02-01", "2023-02-28"),
        ("3月", "2023-03-01", "2023-03-31"),
        ("4月", "2023-04-01", "2023-04-30"),
        ("5月", "2023-05-01", "2023-05-11"),
    ]

    print("\n2022年:")
    total_2022 = 0
    for month_name, m_start, m_end in months_2022:
        m_start_dt = datetime.strptime(m_start, "%Y-%m-%d")
        m_end_dt = datetime.strptime(m_end, "%Y-%m-%d")

        # 特殊处理2月（起始日为2022-02-15）
        if month_name == "2月":
            # 从2022-02-15到2022-02-28
            days_in_month = (m_end_dt - datetime.strptime("2022-02-15", "%Y-%m-%d")).days
        else:
            days_in_month = (m_end_dt - m_start_dt).days + 1

        total_2022 += days_in_month
        print(f"  {month_name}: {days_in_month:2d} 天")

    print(f"\n  2022年合计: {total_2022} 天")

    print("\n2023年:")
    total_2023 = 0
    for month_name, m_start, m_end in months_2023:
        m_start_dt = datetime.strptime(m_start, "%Y-%m-%d")
        m_end_dt = datetime.strptime(m_end, "%Y-%m-%d")
        days_in_month = (m_end_dt - m_start_dt).days + 1
        total_2023 += days_in_month
        print(f"  {month_name}: {days_in_month:2d} 天")

    print(f"\n  2023年合计: {total_2023} 天")

    # 债权人申报表显示：2022年319天，2023年131天，总计450天
    print("\n" + "-" * 70)
    print("债权人申报表数据:")
    print("  2022年: 319 天")
    print("  2023年: 131 天")
    print("  总计:   450 天")

    print("\n本脚本逐月累加:")
    print(f"  2022年: {total_2022} 天")
    print(f"  2023年: {total_2023} 天")
    print(f"  总计:   {total_2022 + total_2023} 天")

    print("\n" + "=" * 70)
    print("最终验证结论")
    print("=" * 70)
    print(f"\n标准计算方法（Python timedelta）: {natural_days} 天")
    print(f"逐月累加验证结果: {total_2022 + total_2023} 天")

    if natural_days == 451 and (total_2022 + total_2023) == 451:
        print("\n✓✓✓ 双重验证确认: 正确天数为 451 天")
        print("\nAgent系统计算结果正确！")
        print("债权人申报的450天和律师审阅的452天均有误差。")

    print("\n" + "=" * 70)


if __name__ == "__main__":
    main()
