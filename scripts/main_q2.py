from pathlib import Path
import pandas as pd

from optimization.q2_optimizer import optimize_day
from utils.battery import Battery
from utils.data_loader import DataLoader
from utils.q2_plotting import (
    plot_representative_day,
    plot_annual_statistics,
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
    print("问题二：全年储能优化调度")
    print("=" * 60)

    loader = DataLoader(DATA_FOLDER)

    attachment2 = loader.load_attachment2()
    year_data = loader.split_into_days(attachment2)

    print(f"\n成功读取全年数据：{len(year_data)} 天")

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

    daily_summary = []

    planned_purchase_all = []
    emergency_purchase_all = []
    charge_all = []
    discharge_all = []
    storage_all = []
    curtailment_all = []

    # --------------------------------------------------
    # Annual optimization
    # --------------------------------------------------

    for i, day in enumerate(year_data):

        result = optimize_day(
            price=price,
            load_kw=day["load"],
            pv_kw=day["pv"],
            battery=battery,
            initial_energy=current_soc,
        )

        current_soc = result["end_energy"]

        planned_purchase_all.append(result["planned_purchase"] * dt)
        emergency_purchase_all.append(result["emergency_purchase"] * dt)
        charge_all.append(result["charge"] * dt)
        discharge_all.append(result["discharge"] * dt)
        storage_all.append(result["storage"])
        curtailment_all.append(result["curtailment"] * dt)

        current_date = str(day["date"].date())

        for season, target in representative_days.items():
            if current_date == target:
                representative_results[season] = {
                    "load": day["load"],
                    "pv": day["pv"],
                    "grid": result["planned_purchase"] * 6,
                    "charge": result["charge"] * 6,
                    "discharge": result["discharge"] * 6,
                }

        daily_summary.append({
            "日期": day["date"].date(),
            "购电成本(元)": result["total_cost"],
            "正常购电成本(元)": result["normal_cost"],
            "应急购电成本(元)": result["emergency_cost"],
            "计划购电量(kWh)": result["planned_purchase"].sum() * dt,
            "应急购电量(kWh)": result["emergency_purchase"].sum() * dt,
            "弃光量(kWh)": result["curtailment"].sum() * dt,
            "日终SOC(kWh)": current_soc,
        })

        if (i + 1) % 50 == 0:
            print(f"已完成 {i+1}/{len(year_data)} 天")

    summary_df = pd.DataFrame(daily_summary)

    # --------------------------------------------------
    # Export starts from Feb 1
    # --------------------------------------------------

    start_idx = summary_df[
        summary_df["日期"].astype(str) == "2025-02-01"
    ].index[0]

    summary_export = summary_df.iloc[start_idx:].reset_index(drop=True)

    planned_purchase_export = planned_purchase_all[start_idx:]
    emergency_export = emergency_purchase_all[start_idx:]
    charge_export = charge_all[start_idx:]
    discharge_export = discharge_all[start_idx:]
    storage_export = storage_all[start_idx:]

    # --------------------------------------------------
    # Sheet 1
    # --------------------------------------------------

    time_labels = [
        f"{(10*(i+1))//60:02d}:{(10*(i+1))%60:02d}"
        for i in range(144)
    ]

    planned_purchase_df = pd.DataFrame(
        planned_purchase_export,
        columns=time_labels,
    )

    planned_purchase_df.insert(0, "日期", summary_export["日期"])

    # --------------------------------------------------
    # Sheet 2
    # --------------------------------------------------

    periods = [
        "0:00-4:00",
        "4:00-8:00",
        "8:00-12:00",
        "12:00-16:00",
        "16:00-20:00",
        "20:00-24:00",
    ]

    charge_summary = []

    for day_idx in range(len(summary_export)):

        charge = charge_export[day_idx]
        discharge = discharge_export[day_idx]
        soc = storage_export[day_idx]

        for block in range(6):

            s = block * 24
            e = s + 24

            row = {
                "日期": summary_export.iloc[day_idx]["日期"] if block == 0 else "",
                "时间段": periods[block],
                "充电量": float(charge[s:e].sum()),
                "放电量": float(discharge[s:e].sum()),
                "时刻": "",
                "储电量": "",
            }

            if block == 0:
                row["时刻"] = "0:00"
                row["储电量"] = float(soc[0])

            if block == 5:
                row["时刻"] = "24:00"
                row["储电量"] = float(soc[-1])

            charge_summary.append(row)

    charge_summary_df = pd.DataFrame(charge_summary)

    # --------------------------------------------------
    # Sheet 3
    # --------------------------------------------------

    emergency_rows = []

    for day_idx in range(len(summary_export)):

        emergency = emergency_export[day_idx]
        date = summary_export.iloc[day_idx]["日期"]

        has_event = False

        for i, value in enumerate(emergency):

            if value > 1e-6:

                sh = (i * 10) // 60
                sm = (i * 10) % 60
                eh = ((i + 1) * 10) // 60
                em = ((i + 1) * 10) % 60

                emergency_rows.append({
                    "日期": date,
                    "紧急购电时间段": f"{sh:02d}:{sm:02d}-{eh:02d}:{em:02d}",
                    "紧急购电量": float(value),
                })

                has_event = True

        if not has_event:
            emergency_rows.append({
                "日期": date,
                "紧急购电时间段": "",
                "紧急购电量": "",
            })

    emergency_df = pd.DataFrame(emergency_rows)

    # --------------------------------------------------
    # Export ONLY result2.xlsx
    # --------------------------------------------------

    with pd.ExcelWriter(
        RESULTS_FOLDER / "result2.xlsx",
        engine="openpyxl",
    ) as writer:

        planned_purchase_df.to_excel(
            writer,
            sheet_name="计划购电量",
            index=False,
        )

        charge_summary_df.to_excel(
            writer,
            sheet_name="充放电量",
            index=False,
        )

        emergency_df.to_excel(
            writer,
            sheet_name="紧急购电量",
            index=False,
        )

    # --------------------------------------------------
    # Representative-day figures
    # --------------------------------------------------

    for season, data in representative_results.items():

        plot_representative_day(
            day_name=season,
            load=data["load"],
            pv=data["pv"],
            grid=data["grid"],
            charge=data["charge"],
            discharge=data["discharge"],
            save_path=FIGURE_FOLDER / f"图2-1_{season}典型日优化调度图.png",
        )

    # --------------------------------------------------
    # Annual figures
    # --------------------------------------------------

    plot_storage_df = pd.DataFrame(
        storage_all,
        columns=["00:00"] + time_labels,
    )

    plot_storage_df.insert(0, "日期", summary_df["日期"])

    plot_annual_statistics(
        summary_df,
        plot_storage_df,
        FIGURE_FOLDER,
    )

    # --------------------------------------------------
    # Summary
    # --------------------------------------------------

    print("\n" + "=" * 60)
    print("全年优化完成！")
    print("=" * 60)

    print(f"全年总购电成本：{summary_df['购电成本(元)'].sum():.2f} 元")
    print(f"全年计划购电量：{summary_df['计划购电量(kWh)'].sum():.2f} kWh")
    print(f"全年应急购电量：{summary_df['应急购电量(kWh)'].sum():.2f} kWh")
    print(f"全年弃光量：{summary_df['弃光量(kWh)'].sum():.2f} kWh")

    print("\n已生成：result2.xlsx")


if __name__ == "__main__":
    main()