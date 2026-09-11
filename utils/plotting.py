
import matplotlib.pyplot as plt

plt.rcParams["font.sans-serif"] = [
    "Microsoft YaHei",
    "SimHei",
]

plt.rcParams["axes.unicode_minus"] = False


def plot_battery_soc(
    energy,
    output_path,
):
    plt.figure(figsize=(10, 5))

    plt.plot(
        energy,
        linewidth=2.5,
    )

    plt.axhline(
        1200,
        linestyle="--",
        alpha=0.6,
        label="最低储电量",
    )

    plt.axhline(
        10800,
        linestyle="--",
        alpha=0.6,
        label="最高储电量",
    )

    plt.title("电池荷电状态变化曲线")

    plt.xlabel("时间步")

    plt.ylabel("储能/kWh")

    plt.legend()

    plt.grid(alpha=0.3)

    plt.tight_layout()

    plt.savefig(
        output_path,
        dpi=300,
    )

    plt.close()