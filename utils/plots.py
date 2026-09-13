import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

plt.rcParams["font.sans-serif"]=["Microsoft YaHei"]
plt.rcParams["axes.unicode_minus"]=False


def plot_q4_price(price_matrix, save_path):
    plt.figure(figsize=(10,4))
    plt.plot(price_matrix.flatten(),linewidth=0.4)
    plt.xlabel("10分钟时段")
    plt.ylabel("电价(元/kWh)")
    plt.title("图4-1 全年波动电价变化")
    plt.tight_layout()
    plt.savefig(save_path,dpi=300)
    plt.close()


def plot_cost_comparison(q2,q3,q42,q43,save_path):
    labels=["问题二","问题三","问题四(2)","问题四(3)"]
    values=np.array([q2,q3,q42,q43])/10000

    plt.figure(figsize=(7,5))
    bars=plt.bar(labels,values)

    for b,v in zip(bars,values):
        plt.text(b.get_x()+b.get_width()/2,v+5,f"{v:.1f}",
                 ha="center",fontsize=10)

    plt.ylabel("总费用(万元)")
    plt.title("图4-4 四种策略全年成本比较")
    plt.tight_layout()
    plt.savefig(save_path,dpi=300)
    plt.close()


def plot_month_compare(df42,df43,save_path):

    month42=df42.groupby(df42["日期"].dt.month)["购电成本(元)"].sum()/10000
    month43=df43.groupby(df43["日期"].dt.month)["购电成本(元)"].sum()/10000

    x=np.arange(len(month42))
    w=0.35

    plt.figure(figsize=(10,5))
    plt.bar(x-w/2,month42,width=w,label="问题4(2)")
    plt.bar(x+w/2,month43,width=w,label="问题4(3)")

    plt.xticks(x,month42.index)
    plt.xlabel("月份")
    plt.ylabel("费用(万元)")
    plt.legend()
    plt.title("图4-5 波动电价两种策略月度成本比较")
    plt.tight_layout()
    plt.savefig(save_path,dpi=300)
    plt.close()


def plot_month_purchase(summary_df,save_path):

    month=summary_df.groupby(summary_df["日期"].dt.month)["计划购电量(kWh)"].sum()/1000

    plt.figure(figsize=(9,4))
    plt.bar(month.index,month.values)
    plt.xlabel("月份")
    plt.ylabel("购电量(MWh)")
    plt.title("图2-6 全年月度计划购电量")
    plt.tight_layout()
    plt.savefig(save_path,dpi=300)
    plt.close()


def plot_soc_box(storage_df,save_path):

    months=pd.to_datetime(storage_df["日期"]).dt.month
    soc=storage_df.iloc[:,1:].mean(axis=1)

    data=[soc[months==m] for m in range(1,13)]

    plt.figure(figsize=(10,5))
    plt.boxplot(data,labels=range(1,13),showfliers=False)
    plt.xlabel("月份")
    plt.ylabel("平均SOC(kWh)")
    plt.title("图2-7 月平均SOC分布")
    plt.tight_layout()
    plt.savefig(save_path,dpi=300)
    plt.close()