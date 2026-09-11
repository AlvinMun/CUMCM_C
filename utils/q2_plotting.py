
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
    """
    Draw the representative-day scheduling figure.

    Parameters
    ----------
    load : ndarray(144,)
    pv : ndarray(144,)
    grid : ndarray(144,)
    charge : ndarray(144,)
    discharge : ndarray(144,)
    """

    hours = np.arange(144) / 6

    plt.figure(figsize=(10, 6))

    plt.plot(
        hours,
        load,
        label="小区负荷",
        linewidth=2,
    )

    plt.plot(
        hours,
        pv,
        label="光伏发电",
        linewidth=2,
    )

    plt.plot(
        hours,
        grid,
        label="计划购电",
        linewidth=2,
    )

    plt.plot(
        hours,
        charge,
        label="电池充电",
        linewidth=2,
    )

    plt.plot(
        hours,
        discharge,
        label="电池放电",
        linewidth=2,
    )

    plt.xlim(0, 24)

    plt.xticks(np.arange(0, 25, 4))

    plt.xlabel("时间 / h")

    plt.ylabel("功率 / kW")

    plt.title(f"{day_name}典型日优化调度结果")

    plt.grid(alpha=0.3)

    plt.legend()

    plt.tight_layout()

    save_path = Path(save_path)

    save_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    plt.savefig(
        save_path,
        dpi=300,
        bbox_inches="tight",
    )

    plt.close()