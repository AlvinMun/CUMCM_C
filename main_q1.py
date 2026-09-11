from pathlib import Path

from optimization.q1_optimizer import optimize_day
from utils.battery import Battery
from utils.data_loader import DataLoader
from utils.excel_export import export_question1
from utils.q1_plotting import plot_battery_soc

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

    # Load data
    loader = DataLoader(DATA_FOLDER)

    df = loader.clean_columns(
        loader.load_attachment1()
    )

    print("\n附件1读取成功！")
    print(df.head())


    # Official battery parameters
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


    # Solve optimization
    result = optimize_day(
        price,
        load,
        pv,
        battery,
    )

 
    # Extract optimization results
    grid_purchase = result["grid_purchase"]
    charge = result["charge"]
    discharge = result["discharge"]
    battery_energy = result["battery_energy"]
    total_cost = result["total_cost"]


    # Plot SOC curve
    plot_battery_soc(
        battery_energy,
        FIGURE_FOLDER / "图1_电池荷电状态变化曲线.png",
    )

    # Export official Excel
    export_question1(
        DATA_FOLDER / "result1.xlsx",
        RESULTS_FOLDER / "问题一优化结果.xlsx",
        grid_purchase,
        total_cost,
        charge,
        discharge,
        battery_energy,
    )

    # Print summary
    print("\n优化完成！")
    print(f"优化状态：{result['message']}")

    print(f"全天购电成本：{total_cost:.2f} 元")
    print(f"全天购電量：{grid_purchase.sum():.2f} kWh")

    print("\n图表已生成：")
    print(" - 图1_电池荷电状态变化曲线.png")

    print("\n结果文件已生成：")
    print(" - 问题一优化结果.xlsx")

    print("\n问题一完成！")
    print("=" * 60)


if __name__ == "__main__":
    main()