
from pathlib import Path
from utils.data_loader import DataLoader

loader = DataLoader(Path("data"))

attachment2 = loader.load_attachment2()

days = loader.split_into_days(attachment2)

print(f"全年天数：{len(days)}")

print(f"第一天：{days[0]['date'].date()}")

print(f"负荷数据点数：{len(days[0]['load'])}")

print(f"光伏数据点数：{len(days[0]['pv'])}")

print("\n第一天前5个负荷值：")
print(days[0]["load"][:5])

print("\n第一天前5个光伏值：")
print(days[0]["pv"][:5])