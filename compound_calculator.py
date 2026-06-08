#!/usr/bin/env python3
"""
纳指定投复利计算器
用法：
  python compound_calculator.py                                          # 默认参数
  python compound_calculator.py --start-age 25 --annual 250000 --increase 50000 --stop-age 35 --rate 0.12
  python compound_calculator.py --rate 0.10                              # 保守估计 10%
  python compound_calculator.py --rate 0.15                              # 乐观估计 15%
  python compound_calculator.py --end-age 60                             # 展示到 60 岁
"""
import argparse


def calc_compound(start_age, annual_first, annual_increase, stop_age, rate, end_age):
    """计算投入期 + 停止投入后的复利增长"""
    results = []
    total_asset = 0.0
    total_invested = 0.0

    # 阶段一：投入期（start_age ~ stop_age）
    for age in range(start_age, stop_age + 1):
        year_num = age - start_age  # 第几年（0-indexed）
        yearly_invest = annual_first + annual_increase * year_num
        total_invested += yearly_invest
        # 年初资产 + 当年投入，一起计算当年收益
        total_asset = (total_asset + yearly_invest) * (1 + rate)
        results.append({
            "age": age,
            "phase": "投入期",
            "yearly_invest": yearly_invest,
            "total_invested": total_invested,
            "total_asset": total_asset,
            "profit": total_asset - total_invested,
            "profit_pct": (total_asset / total_invested - 1) * 100,
        })

    # 阶段二：停止投入，纯复利增长（stop_age+1 ~ end_age）
    for age in range(stop_age + 1, end_age + 1):
        total_asset = total_asset * (1 + rate)
        results.append({
            "age": age,
            "phase": "复利期",
            "yearly_invest": 0,
            "total_invested": total_invested,
            "total_asset": total_asset,
            "profit": total_asset - total_invested,
            "profit_pct": (total_asset / total_invested - 1) * 100,
        })

    return results


def fmt(val):
    """格式化金额：万元"""
    return f"{val / 10000:>10,.0f}万"


def print_report(results, rate):
    """打印复利增长报告"""
    print("=" * 72)
    print(f"  纳指定投复利计算器 — 年化 {rate*100:.0f}%")
    print("=" * 72)

    # 投入期
    print(f"\n{'年龄':>4} {'阶段':<6} {'年投入':>10} {'累计投入':>10} {'总资产':>10} {'收益':>10} {'收益率':>8}")
    print(f"{'─'*4} {'─'*6} {'─'*10} {'─'*10} {'─'*10} {'─'*10} {'─'*8}")

    invest_rows = [r for r in results if r["phase"] == "投入期"]
    compound_rows = [r for r in results if r["phase"] == "复利期"]

    for r in invest_rows:
        inv = f"{r['yearly_invest']/10000:>9.0f}万" if r["yearly_invest"] else ""
        print(f"{r['age']:>4} {r['phase']:<6} {inv} {fmt(r['total_invested'])} "
              f"{fmt(r['total_asset'])} {fmt(r['profit'])} {r['profit_pct']:>7.1f}%")

    # 分割线
    print(f"{'─'*72}")
    print(f"  ↑ 停止投入，以下为纯复利增长（不再追加投入）")
    print(f"{'─'*72}")

    # 复利期 — 每5年打印一次 + 最后一行
    compound_ages = set()
    for r in compound_rows:
        # 每5年打印
        if (r["age"] - invest_rows[-1]["age"]) % 5 == 0:
            compound_ages.add(r["age"])
    if compound_rows:
        compound_ages.add(compound_rows[-1]["age"])  # 确保最后一行

    for r in compound_rows:
        if r["age"] in compound_ages:
            multiplier = r["total_asset"] / r["total_invested"]
            print(f"{r['age']:>4} {r['phase']:<6} {'':>10} {fmt(r['total_invested'])} "
                  f"{fmt(r['total_asset'])} {fmt(r['profit'])} "
                  f"{r['profit_pct']:>7.1f}% ×{multiplier:.1f}")

    # 汇总
    last = results[-1]
    first_invest = results[0]["yearly_invest"]
    invest_years = len(invest_rows)
    print(f"\n{'═'*72}")
    print(f"  汇总:")
    print(f"    投入期: {invest_years}年 ({invest_rows[0]['age']}~{invest_rows[-1]['age']}岁)")
    print(f"    首年投入: {first_invest/10000:.0f}万，每年递增{(results[1]['yearly_invest']-first_invest)/10000:.0f}万")
    print(f"    累计投入: {last['total_invested']/10000:,.0f}万")
    print(f"    最终资产: {last['total_asset']/10000:,.0f}万 ({last['age']}岁)")
    print(f"    总收益:   {last['profit']/10000:,.0f}万 (翻了 {last['total_asset']/last['total_invested']:.1f} 倍)")
    print(f"    年化收益: {rate*100:.0f}%")
    print(f"{'═'*72}")


def main():
    parser = argparse.ArgumentParser(description="纳指定投复利计算器")
    parser.add_argument("--start-age", type=int, default=25, help="开始投入年龄（默认25）")
    parser.add_argument("--annual", type=int, default=250000, help="首年投入金额（默认25万）")
    parser.add_argument("--increase", type=int, default=50000, help="每年递增金额（默认5万）")
    parser.add_argument("--stop-age", type=int, default=34, help="停止投入年龄（默认34，即25~34岁投入10年）")
    parser.add_argument("--end-age", type=int, default=60, help="展示到多少岁（默认60）")
    parser.add_argument("--rate", type=float, default=0.12, help="年化收益率（默认0.12即12%%）")
    args = parser.parse_args()

    results = calc_compound(
        start_age=args.start_age,
        annual_first=args.annual,
        annual_increase=args.increase,
        stop_age=args.stop_age,
        rate=args.rate,
        end_age=args.end_age,
    )

    print_report(results, args.rate)


if __name__ == "__main__":
    main()
