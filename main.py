
from pathlib import Path

from optimization.q1_optimizer import optimize_day
from utils.battery import Battery
from utils.data_loader import DataLoader
from utils.excel_export import export_question1
from utils.plotting import plot_battery_soc

PROJECT_ROOT = Path(__file__).resolve().parent

DATA_FOLDER = PROJECT_ROOT / "data"
RESULTS_FOLDER = PROJECT_ROOT / "results"
FIGURE_FOLDER = PROJECT_ROOT / "figures"

RESULTS_FOLDER.mkdir(exist_ok=True)
FIGURE_FOLDER.mkdir(exist_ok=True)


def main():

    print("=" * 60)
    print("CUMCM 2026 国赛 C题")
    print("问题一：微网最优购电调度")
    print("=" * 60)

    loader = DataLoader(DATA_FOLDER)

    df = loader.clean_columns(
        loader.load_attachment1()
    )

    print("\n附件1读取成功！")
    print(df.head())

    battery = Battery(
        capacity=12000,
        initial_energy=6000,
        max_charge_power=5000,
        max_discharge_power=5000,
        charge_efficiency=0.90,
        discharge_efficiency=0.90,
    )

    price = df["电价"].to_numpy()

    load = df["小区负载"].to_numpy()

    pv = df["光伏发电预测功率"].to_numpy()

    result = optimize_day(
        price,
        load,
        pv,
        battery,
    )

    grid = result["grid_purchase"]
    energy = result["battery_energy"]
    cost = result["total_cost"]

    plot_battery_soc(
        energy,
        FIGURE_FOLDER / "图1_电池荷电状态变化曲线.png",
    )

    export_question1(
        DATA_FOLDER / "result1.xlsx",
        RESULTS_FOLDER / "问题一优化结果.xlsx",
        grid,
        cost,
    )

    print("\n优化完成！")
    print(result["message"])

    print(f"全天购电成本：{cost:.2f} 元")
    print(f"全天购电量：{grid.sum():.2f} kWh")

    print("\n图表已生成：")
    print(" - 图1_电池荷电状态变化曲线.png")

    print("\n结果文件已生成：")
    print(" - 问题一优化结果.xlsx")

    print("\n问题一完成！")
    print("=" * 60)


if __name__ == "__main__":
    main()