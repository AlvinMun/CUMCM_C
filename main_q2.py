from pathlib import Path
import pandas as pd

from optimization.q2_optimizer import optimize_day_q2
from utils.battery import Battery
from utils.data_loader import DataLoader
from utils.q2_plotting import plot_representative_day

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

    # -------------------------------------------------
    # Read official Attachment 2
    # -------------------------------------------------

    loader = DataLoader(DATA_FOLDER)

    attachment2 = loader.load_attachment2()
    days = loader.split_into_days(attachment2)

    print(f"\n成功读取全年数据：{len(days)} 天")

    # -------------------------------------------------
    # Electricity price (same 144-point profile every day)
    # -------------------------------------------------

    price = loader.load_attachment1()["电价"].to_numpy()

    # -------------------------------------------------
    # Official battery parameters
    # -------------------------------------------------

    battery = Battery(
        capacity=12000,
        initial_energy=6000,
        max_charge_power=5000,
        max_discharge_power=5000,
        charge_efficiency=0.90,
        discharge_efficiency=0.90,
    )

    current_soc = battery.initial_energy

    # -------------------------------------------------
    # Representative days
    # -------------------------------------------------

    representative_days = {
        "春分": "2025-03-20",
        "夏至": "2025-06-21",
        "秋分": "2025-09-23",
        "冬至": "2025-12-21",
    }

    representative_results = {}

    # -------------------------------------------------
    # Storage containers
    # -------------------------------------------------

    daily_results = []

    planned_purchase_all = []
    emergency_purchase_all = []
    charge_all = []
    discharge_all = []
    storage_all = []
    curtailment_all = []

    # -------------------------------------------------
    # Optimize each day
    # -------------------------------------------------

    for i, day in enumerate(days):

        result = optimize_day_q2(
            price=price,
            load_kw=day["load"],
            pv_kw=day["pv"],
            battery=battery,
            initial_energy=current_soc,
        )

        current_soc = result["end_energy"]

        planned_purchase_all.append(result["planned_purchase"])
        emergency_purchase_all.append(result["emergency_purchase"])
        charge_all.append(result["charge"])
        discharge_all.append(result["discharge"])
        storage_all.append(result["storage"])
        curtailment_all.append(result["curtailment"])

        # Save representative-day data
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

        daily_results.append({
            "日期": day["date"].date(),
            "购电成本(元)": result["total_cost"],
            "正常购电成本(元)": result["normal_cost"],
            "应急购电成本(元)": result["emergency_cost"],
            "计划购电量(kWh)": result["planned_purchase"].sum(),
            "应急购电量(kWh)": result["emergency_purchase"].sum(),
            "弃光量(kWh)": result["curtailment"].sum(),
            "日终SOC(kWh)": current_soc,
        })

        if (i + 1) % 50 == 0:
            print(f"已完成 {i+1}/{len(days)} 天")

    # -------------------------------------------------
    # Daily summary
    # -------------------------------------------------

    summary = pd.DataFrame(daily_results)

    summary.to_excel(
        RESULTS_FOLDER / "问题二全年优化结果.xlsx",
        index=False,
    )

    # -------------------------------------------------
    # Save complete trajectories
    # -------------------------------------------------

    time_labels = [
        f"{(10*(i+1))//60:02d}:{(10*(i+1))%60:02d}"
        for i in range(144)
    ]

    storage_labels = ["00:00"] + time_labels

    planned_purchase_df = pd.DataFrame(
        planned_purchase_all,
        columns=time_labels,
    )

    emergency_purchase_df = pd.DataFrame(
        emergency_purchase_all,
        columns=time_labels,
    )

    charge_df = pd.DataFrame(
        charge_all,
        columns=time_labels,
    )

    discharge_df = pd.DataFrame(
        discharge_all,
        columns=time_labels,
    )

    curtailment_df = pd.DataFrame(
        curtailment_all,
        columns=time_labels,
    )

    storage_df = pd.DataFrame(
        storage_all,
        columns=storage_labels,
    )

    for df in [
        planned_purchase_df,
        emergency_purchase_df,
        charge_df,
        discharge_df,
        curtailment_df,
        storage_df,
    ]:
        df.insert(0, "日期", summary["日期"])

    planned_purchase_df.to_excel(
        RESULTS_FOLDER / "问题二计划购电轨迹.xlsx",
        index=False,
    )

    emergency_purchase_df.to_excel(
        RESULTS_FOLDER / "问题二应急购电轨迹.xlsx",
        index=False,
    )

    charge_df.to_excel(
        RESULTS_FOLDER / "问题二充电轨迹.xlsx",
        index=False,
    )

    discharge_df.to_excel(
        RESULTS_FOLDER / "问题二放电轨迹.xlsx",
        index=False,
    )

    storage_df.to_excel(
        RESULTS_FOLDER / "问题二SOC轨迹.xlsx",
        index=False,
    )

    curtailment_df.to_excel(
        RESULTS_FOLDER / "问题二弃光轨迹.xlsx",
        index=False,
    )

    # -------------------------------------------------
    # Generate representative-day figures
    # -------------------------------------------------

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

    # -------------------------------------------------
    # Final summary
    # -------------------------------------------------

    print("\n" + "=" * 60)
    print("全年优化完成！")
    print("=" * 60)

    print(f"全年总购电成本：{summary['购电成本(元)'].sum():.2f} 元")
    print(f"全年计划购电量：{summary['计划购电量(kWh)'].sum():.2f} kWh")
    print(f"全年应急购电量：{summary['应急购电量(kWh)'].sum():.2f} kWh")
    print(f"全年弃光量：{summary['弃光量(kWh)'].sum():.2f} kWh")
    print(f"年末SOC：{current_soc:.2f} kWh")

    print("\n已生成文件：")
    print(" - 问题二全年优化结果.xlsx")
    print(" - 问题二计划购电轨迹.xlsx")
    print(" - 问题二应急购电轨迹.xlsx")
    print(" - 问题二充电轨迹.xlsx")
    print(" - 问题二放电轨迹.xlsx")
    print(" - 问题二SOC轨迹.xlsx")
    print(" - 问题二弃光轨迹.xlsx")

    print("\n已生成图表：")
    print(" - 图2-1_春分典型日优化调度图.png")
    print(" - 图2-1_夏至典型日优化调度图.png")
    print(" - 图2-1_秋分典型日优化调度图.png")
    print(" - 图2-1_冬至典型日优化调度图.png")


if __name__ == "__main__":
    main()