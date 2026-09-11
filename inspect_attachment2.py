from pathlib import Path
import pandas as pd

file = Path("data") / "附件2.xlsx"

xls = pd.ExcelFile(file)

print("工作表：")
print(xls.sheet_names)

for sheet in xls.sheet_names:
    print("\n" + "="*50)
    print(sheet)
    df = pd.read_excel(file, sheet_name=sheet)
    print("列名：")
    print(df.columns.tolist())
    print("\n前5行：")
    print(df.head())