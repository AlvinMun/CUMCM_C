from pathlib import Path
import pandas as pd

from optimization.q3_optimizer import optimize_day_q3
from utils.battery import Battery
from utils.data_loader import DataLoader
from utils.q2_plotting import (
    plot_representative_day,
    plot_annual_statistics,
)
from utils.q3_plotting import (
    plot_forecast_updates,
    plot_monthly_adjustment,
    plot_plan_vs_adjust,
)

PROJECT_ROOT = Path(__file__).resolve().parent

DATA_FOLDER = PROJECT_ROOT / "data"
RESULTS_FOLDER = PROJECT_ROOT / "results"
FIGURE_FOLDER = PROJECT_ROOT / "figures"

RESULTS_FOLDER.mkdir(exist_ok=True)
FIGURE_FOLDER.mkdir(exist_ok=True)


def main():

    print("=" * 60)
    print("CUMCM 2026 国赛 C题")
    print("问题三：滚动预测购电优化")
    print("=" * 60)

    loader = DataLoader(DATA_FOLDER)

    attachment2 = loader.load_attachment2()
    forecast_data = loader.load_attachment3()
    year_data = loader.split_into_days(attachment2)

    price = loader.load_attachment1()["电价"].to_numpy()

    battery = Battery(
        capacity=12000,
        initial_energy=6000,
        max_charge_power=5000,
        max_discharge_power=5000,
        charge_efficiency=0.90,
        discharge_efficiency=0.90,
    )

    current_soc = battery.initial_energy
    dt = 1 / 6

    representative_days = {
        "春分": "2025-03-20",
        "夏至": "2025-06-21",
        "秋分": "2025-09-23",
        "冬至": "2025-12-21",
    }

    representative_results = {}

    summary = []

    plan_all = []
    adjusted_all = []
    charge_all = []
    discharge_all = []
    storage_all = []

    emergency_events = []

    daily_adjust_costs = []
    daily_dates = []

    sample_day = None
    sample_forecast = None
    sample_result = None

    # --------------------------------------------------
    # Rolling optimization
    # --------------------------------------------------

    for i in range(len(year_data)):

        day = year_data[i]
        forecast = forecast_data[i]

        result = optimize_day_q3(
            price=price,
            load_kw=day["load"],
            pv_actual_kw=day["pv"],
            forecasts=forecast["forecast"],
            battery=battery,
            initial_energy=current_soc,
        )

        current_soc = result["end_energy"]

        plan_all.append(result["planned_purchase"] * dt)
        adjusted_all.append(result["adjusted_purchase"] * dt)
        charge_all.append(result["charge"] * dt)
        discharge_all.append(result["discharge"] * dt)
        storage_all.append(result["storage"])

        daily_adjust_costs.append(result["adjustment_cost"])
        daily_dates.append(day["date"])

        date = day["date"].date()

        summary.append({
            "日期": date,
            "计划购电费": result["normal_cost"],
            "调整费用": result["adjustment_cost"],
            "紧急购电费": result["emergency_cost"],
            "总费用": result["total_cost"],
            "日终SOC": current_soc,
        })

        emergency = result["emergency_purchase"] * dt

        for t, value in enumerate(emergency):

            if value > 1e-6:

                sh = (t * 10) // 60
                sm = (t * 10) % 60
                eh = ((t + 1) * 10) // 60
                em = ((t + 1) * 10) % 60

                emergency_events.append({
                    "日期": date,
                    "紧急购电时间段": f"{sh:02d}:{sm:02d}-{eh:02d}:{em:02d}",
                    "紧急购电量": float(value),
                })

        current_date = str(date)

        if current_date == "2025-03-20":
            sample_day = day
            sample_forecast = forecast["forecast"]
            sample_result = result

        if current_date in representative_days.values():

            season = [
                k for k, v in representative_days.items()
                if v == current_date
            ][0]

            representative_results[season] = {
                "load": day["load"],
                "pv": day["pv"],
                "grid": result["adjusted_purchase"] * 6,
                "charge": result["charge"] * 6,
                "discharge": result["discharge"] * 6,
            }

        if (i + 1) % 50 == 0:
            print(f"已完成 {i+1}/365 天")

    summary_df = pd.DataFrame(summary)

    # --------------------------------------------------
    # Export (official template starts Feb 1)
    # --------------------------------------------------

    start = summary_df[
        summary_df["日期"].astype(str) == "2025-02-01"
    ].index[0]

    summary_export = summary_df.iloc[start:].reset_index(drop=True)

    plan_export = plan_all[start:]
    adjusted_export = adjusted_all[start:]
    charge_export = charge_all[start:]
    discharge_export = discharge_all[start:]
    storage_export = storage_all[start:]

    time_labels = [
        f"{(10*(i+1))//60:02d}:{(10*(i+1))%60:02d}"
        for i in range(144)
    ]

    # ---------- Sheet1 ----------

    plan_df = pd.DataFrame(plan_export, columns=time_labels)
    plan_df.insert(0, "日期", summary_export["日期"])
    plan_df["全天购电量"] = plan_df.iloc[:, 1:].sum(axis=1)
    plan_df["全天购电费"] = summary_export["计划购电费"]

    # ---------- Sheet2 ----------

    adjust_df = pd.DataFrame(adjusted_export, columns=time_labels)
    adjust_df.insert(0, "日期", summary_export["日期"])
    adjust_df["全天购电量"] = adjust_df.iloc[:, 1:].sum(axis=1)
    adjust_df["全天购电费"] = summary_export["总费用"]

    # ---------- Sheet3 ----------

    periods = [
        "0:00-4:00",
        "4:00-8:00",
        "8:00-12:00",
        "12:00-16:00",
        "16:00-20:00",
        "20:00-24:00",
    ]

    charge_rows = []

    for d in range(len(summary_export)):

        c = charge_export[d]
        dis = discharge_export[d]
        soc = storage_export[d]

        for b in range(6):

            s = b * 24
            e = s + 24

            row = {
                "日期": summary_export.iloc[d]["日期"] if b == 0 else "",
                "时间段": periods[b],
                "充电量": c[s:e].sum(),
                "放电量": dis[s:e].sum(),
                "时刻": "",
                "储电量": "",
            }

            if b == 0:
                row["时刻"] = "0:00"
                row["储电量"] = soc[0]

            if b == 5:
                row["时刻"] = "24:00"
                row["储电量"] = soc[-1]

            charge_rows.append(row)

    charge_df = pd.DataFrame(charge_rows)

    # ---------- Sheet4 ----------

    emergency_df = pd.DataFrame(emergency_events)

    with pd.ExcelWriter(
        RESULTS_FOLDER / "result3.xlsx",
        engine="openpyxl",
    ) as writer:

        plan_df.to_excel(writer, sheet_name="计划购电量", index=False)
        adjust_df.to_excel(writer, sheet_name="调整购电量", index=False)
        charge_df.to_excel(writer, sheet_name="充放电量", index=False)
        emergency_df.to_excel(writer, sheet_name="紧急购电量", index=False)

    # --------------------------------------------------
    # Figures
    # --------------------------------------------------

    storage_labels = ["00:00"] + time_labels

    plot_storage_df = pd.DataFrame(
        storage_all,
        columns=storage_labels,
    )
    plot_storage_df.insert(0, "日期", summary_df["日期"])

    for season, data in representative_results.items():

        plot_representative_day(
            season,
            data["load"],
            data["pv"],
            data["grid"],
            data["charge"],
            data["discharge"],
            FIGURE_FOLDER / f"图3-4_{season}滚动优化.png",
        )

    # 图3-1
    if sample_day is not None:

        plot_forecast_updates(
            actual_pv=sample_day["pv"],
            forecasts=sample_forecast,
            save_path=FIGURE_FOLDER / "图3-1_滚动预测更新示意图.png",
        )

        plot_plan_vs_adjust(
            planned=sample_result["planned_purchase"],
            adjusted=sample_result["adjusted_purchase"],
            save_path=FIGURE_FOLDER / "图3-3_计划购电与调整购电对比.png",
        )

    # 图3-2
    plot_monthly_adjustment(
        daily_adjust_costs,
        daily_dates,
        FIGURE_FOLDER / "图3-2_月度调整费用分布.png",
    )

    # Annual statistics
    plot_summary = summary_df.rename(columns={
        "总费用": "购电成本(元)",
        "日终SOC": "日终SOC(kWh)",
    }).copy()

    plot_summary["弃光量(kWh)"] = 0.0

    plot_annual_statistics(
        plot_summary,
        plot_storage_df,
        FIGURE_FOLDER,
    )

    print("\n" + "=" * 60)
    print("问题三完成！")
    print("=" * 60)

    print(f"全年总费用：{summary_df['总费用'].sum():.2f} 元")
    print(f"全年调整费用：{summary_df['调整费用'].sum():.2f} 元")
    print(f"全年紧急购电费：{summary_df['紧急购电费'].sum():.2f} 元")

    print("\n已生成：result3.xlsx")


if __name__ == "__main__":
    main()