from pathlib import Path
import pandas as pd

from optimization.q2_optimizer import optimize_day
from utils.battery import Battery
from utils.data_loader import DataLoader
from utils.q2_plotting import (
    plot_representative_day,
    plot_annual_statistics,
)

# Project paths

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

    # Load data
    loader = DataLoader(DATA_FOLDER)

    attachment2 = loader.load_attachment2()
    year_data = loader.split_into_days(attachment2)

    print(f"\n成功读取全年数据：{len(year_data)} 天")

    # Electricity price (same every day)

    price = loader.load_attachment1()["电价"].to_numpy()

    # Battery parameters

    battery = Battery(
        capacity=12000,
        initial_energy=6000,
        max_charge_power=5000,
        max_discharge_power=5000,
        charge_efficiency=0.90,
        discharge_efficiency=0.90,
    )

    current_soc = battery.initial_energy
    dt = 1 / 6  # 10 minutes = 1/6 hour

    # Representative days

    representative_days = {
        "春分": "2025-03-20",
        "夏至": "2025-06-21",
        "秋分": "2025-09-23",
        "冬至": "2025-12-21",
    }

    representative_results = {}

    # Containers

    daily_summary = []

    planned_purchase_all = []
    emergency_purchase_all = []
    charge_all = []
    discharge_all = []
    storage_all = []
    curtailment_all = []

    # Optimize whole year

    for i, day in enumerate(year_data):

        result = optimize_day(
            price=price,
            load_kw=day["load"],
            pv_kw=day["pv"],
            battery=battery,
            initial_energy=current_soc,
        )

        current_soc = result["end_energy"]

        # Store copies and convert power(kW) -> energy(kWh)
        planned_purchase_all.append(result["planned_purchase"].copy() * dt)
        emergency_purchase_all.append(result["emergency_purchase"].copy() * dt)
        charge_all.append(result["charge"].copy() * dt)
        discharge_all.append(result["discharge"].copy() * dt)
        curtailment_all.append(result["curtailment"].copy() * dt)
        storage_all.append(result["storage"].copy())

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

    # Create summary dataframe

    summary_df = pd.DataFrame(daily_summary)

    # Create trajectory dataframes

    time_labels = [
        f"{(10 * (i + 1)) // 60:02d}:{(10 * (i + 1)) % 60:02d}"
        for i in range(144)
    ]

    storage_labels = ["00:00"] + time_labels

    planned_purchase_df = pd.DataFrame(
        data=planned_purchase_all,
        columns=time_labels,
        dtype=float,
    )

    emergency_purchase_df = pd.DataFrame(
        data=emergency_purchase_all,
        columns=time_labels,
        dtype=float,
    )

    charge_df = pd.DataFrame(
        data=charge_all,
        columns=time_labels,
        dtype=float,
    )

    discharge_df = pd.DataFrame(
        data=discharge_all,
        columns=time_labels,
        dtype=float,
    )

    curtailment_df = pd.DataFrame(
        data=curtailment_all,
        columns=time_labels,
        dtype=float,
    )

    storage_df = pd.DataFrame(
        data=storage_all,
        columns=storage_labels,
        dtype=float,
    )

    for df in [
        planned_purchase_df,
        emergency_purchase_df,
        charge_df,
        discharge_df,
        curtailment_df,
        storage_df,
    ]:
        df.insert(0, "日期", summary_df["日期"])

    # Export Excel

    with pd.ExcelWriter(
        RESULTS_FOLDER / "问题二全年优化结果.xlsx",
        engine="openpyxl",
    ) as writer:

        summary_df.to_excel(
            writer,
            sheet_name="全年统计",
            index=False,
        )

        planned_purchase_df.to_excel(
            writer,
            sheet_name="计划购电量",
            index=False,
        )

        charge_df.to_excel(
            writer,
            sheet_name="充电量",
            index=False,
        )

        discharge_df.to_excel(
            writer,
            sheet_name="放电量",
            index=False,
        )

        curtailment_df.to_excel(
            writer,
            sheet_name="弃光量",
            index=False,
        )

        emergency_purchase_df.to_excel(
            writer,
            sheet_name="应急购电量",
            index=False,
        )

        storage_df.to_excel(
            writer,
            sheet_name="储能SOC",
            index=False,
        )

    # Export individual Excel files

    planned_purchase_df.to_excel(
        RESULTS_FOLDER / "问题二计划购电量.xlsx",
        index=False,
    )

    emergency_purchase_df.to_excel(
        RESULTS_FOLDER / "问题二应急购电量.xlsx",
        index=False,
    )

    charge_df.to_excel(
        RESULTS_FOLDER / "问题二充电量.xlsx",
        index=False,
    )

    discharge_df.to_excel(
        RESULTS_FOLDER / "问题二放电量.xlsx",
        index=False,
    )

    storage_df.to_excel(
        RESULTS_FOLDER / "问题二储能SOC.xlsx",
        index=False,
    )

    curtailment_df.to_excel(
        RESULTS_FOLDER / "问题二弃光量.xlsx",
        index=False,
    )

    # Representative-day figures

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

    # Annual figures

    plot_annual_statistics(
        summary_df,
        storage_df,
        FIGURE_FOLDER,
    )

    # Print results

    print("\n" + "=" * 60)
    print("全年优化完成！")
    print("=" * 60)

    print(f"全年总购电成本：{summary_df['购电成本(元)'].sum():.2f} 元")
    print(f"全年计划购电量：{summary_df['计划购电量(kWh)'].sum():.2f} kWh")
    print(f"全年应急购电量：{summary_df['应急购电量(kWh)'].sum():.2f} kWh")
    print(f"全年弃光量：{summary_df['弃光量(kWh)'].sum():.2f} kWh")
    print(f"年末SOC：{current_soc:.2f} kWh")

    print("\n已生成结果文件：")
    print(" - 问题二全年优化结果.xlsx")
    print(" - 问题二计划购电量.xlsx")
    print(" - 问题二应急购电量.xlsx")
    print(" - 问题二充电量.xlsx")
    print(" - 问题二放电量.xlsx")
    print(" - 问题二储能SOC.xlsx")
    print(" - 问题二弃光量.xlsx")

    print("\n已生成图表：")
    print(" - 图2-1_春分典型日优化调度图.png")
    print(" - 图2-1_夏至典型日优化调度图.png")
    print(" - 图2-1_秋分典型日优化调度图.png")
    print(" - 图2-1_冬至典型日优化调度图.png")
    print(" - 图2-5a_全年每日购电成本.png")
    print(" - 图2-5b_全年弃光量.png")
    print(" - 图2-5c_全年储能SOC连续变化.png")
    print(" - 图2-5d_全年储能日终SOC变化.png")


if __name__ == "__main__":
    main()