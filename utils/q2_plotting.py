from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

plt.rcParams["font.sans-serif"] = [
    "Microsoft YaHei",
    "SimHei",
    "Arial Unicode MS",
]

plt.rcParams["axes.unicode_minus"] = False



def plot_representative_day(
    day_name,
    load,
    pv,
    grid,
    charge,
    discharge,
    save_path,
):

    hours = np.arange(144) / 6

    plt.figure(figsize=(10, 6))

    plt.plot(hours, load, label="小区负荷", linewidth=2)
    plt.plot(hours, pv, label="光伏发电", linewidth=2)
    plt.plot(hours, grid, label="计划购电", linewidth=2)
    plt.plot(hours, charge, label="电池充电", linewidth=2)
    plt.plot(hours, discharge, label="电池放电", linewidth=2)

    plt.xlim(0, 24)
    plt.xticks(np.arange(0, 25, 4))

    plt.xlabel("时间 / h")
    plt.ylabel("功率 / kW")
    plt.title(f"{day_name}典型日优化调度结果")

    plt.grid(alpha=0.3)
    plt.legend()

    plt.tight_layout()

    save_path = Path(save_path)
    save_path.parent.mkdir(parents=True, exist_ok=True)

    plt.savefig(save_path, dpi=300, bbox_inches="tight")
    plt.close()



def plot_annual_statistics(summary_df, storage_df, save_folder):

    save_folder = Path(save_folder)
    save_folder.mkdir(exist_ok=True)

    days = np.arange(1, len(summary_df) + 1)


    plt.figure(figsize=(11, 4))

    plt.plot(days, summary_df["购电成本(元)"], linewidth=1.5)

    plt.xlabel("日期序号")
    plt.ylabel("购电成本 / 元")
    plt.title("全年每日购电成本变化")

    plt.grid(alpha=0.3)
    plt.tight_layout()

    plt.savefig(
        save_folder / "图2-5a_全年每日购电成本.png",
        dpi=300,
        bbox_inches="tight",
    )

    plt.close()

    plt.figure(figsize=(11, 4))

    plt.bar(days, summary_df["弃光量(kWh)"], width=1.0)

    plt.xlabel("日期序号")
    plt.ylabel("弃光量 / kWh")
    plt.title("全年弃光量统计")

    plt.grid(axis="y", alpha=0.3)
    plt.tight_layout()

    plt.savefig(
        save_folder / "图2-5b_全年弃光量.png",
        dpi=300,
        bbox_inches="tight",
    )

    plt.close()


    soc_matrix = storage_df.iloc[:, 1:].to_numpy()
    soc = soc_matrix[0].copy()

    for i in range(1, len(soc_matrix)):
        soc = np.concatenate([soc, soc_matrix[i, 1:]])

    hours = np.arange(len(soc)) / 6

    plt.figure(figsize=(12, 4))

    plt.plot(hours, soc, linewidth=1.0)

    plt.xlabel("全年运行时间 / h")
    plt.ylabel("SOC / kWh")
    plt.title("全年储能SOC连续变化")

    plt.ylim(1000, 12000)
    plt.grid(alpha=0.3)
    plt.tight_layout()

    plt.savefig(
        save_folder / "图2-5c_全年储能SOC连续变化.png",
        dpi=300,
        bbox_inches="tight",
    )

    plt.close()


    plt.figure(figsize=(11, 4))

    plt.plot(
        days,
        summary_df["日终SOC(kWh)"],
        linewidth=1.8,
    )

    plt.xlabel("日期序号")
    plt.ylabel("日终SOC / kWh")
    plt.title("全年储能日终SOC变化")

    plt.ylim(1000, 12000)
    plt.grid(alpha=0.3)
    plt.tight_layout()

    plt.savefig(
        save_folder / "图2-5d_全年储能日终SOC变化.png",
        dpi=300,
        bbox_inches="tight",
    )

    plt.close()