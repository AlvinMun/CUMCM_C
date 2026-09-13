
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

plt.rcParams["font.sans-serif"] = ["Microsoft YaHei"]
plt.rcParams["axes.unicode_minus"] = False


def plot_forecast_updates(actual_pv, forecasts, save_path):
    """图3-1：滚动预测更新示意图"""

    t = np.arange(144) / 6

    plt.figure(figsize=(10,5))

    plt.plot(t, actual_pv, label="实际光伏", linewidth=2)
    plt.plot(t, forecasts["0:00"], "--", label="0:00预测")
    plt.plot(t, forecasts["6:00"], "--", label="6:00预测")
    plt.plot(t, forecasts["12:00"], "--", label="12:00预测")
    plt.plot(t, forecasts["18:00"], "--", label="18:00预测")

    plt.xlabel("时间(h)")
    plt.ylabel("光伏功率(kW)")
    plt.title("图3-1 滚动预测更新示意图")
    plt.legend()
    plt.grid(alpha=0.3)

    plt.tight_layout()
    plt.savefig(save_path,dpi=300)
    plt.close()


def plot_monthly_adjustment(daily_adjust_costs, dates, save_path):
    """图3-2：月度调整费用"""

    df = pd.DataFrame({
        "date":pd.to_datetime(dates),
        "cost":daily_adjust_costs
    })

    monthly = df.groupby(df["date"].dt.month)["cost"].sum()

    plt.figure(figsize=(9,4))

    plt.bar(monthly.index, monthly.values/10000)

    plt.xlabel("月份")
    plt.ylabel("调整费用(万元)")
    plt.title("图3-2 月度调整费用分布")

    plt.xticks(range(1,13))

    plt.tight_layout()
    plt.savefig(save_path,dpi=300)
    plt.close()


def plot_plan_vs_adjust(planned, adjusted, save_path):
    """图3-3：计划购电 vs 调整后购电"""

    t=np.arange(144)/6

    plt.figure(figsize=(10,4))

    plt.plot(t, planned*6,label="计划购电")
    plt.plot(t, adjusted*6,label="调整后购电")

    plt.xlabel("时间(h)")
    plt.ylabel("购电功率(kW)")
    plt.title("图3-3 计划购电与调整后购电对比")
    plt.legend()
    plt.grid(alpha=0.3)

    plt.tight_layout()
    plt.savefig(save_path,dpi=300)
    plt.close()