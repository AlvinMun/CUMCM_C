
from openpyxl import load_workbook
import numpy as np


def export_question1(
    template_path,
    output_path,
    grid_purchase,
    total_cost,
    charge=None,
    discharge=None,
    battery_energy=None,
):
    """
    Export Question 1 results into the official template.

    Sheet1:
        144 time intervals.

    Sheet2:
        Six 4-hour summaries.
    """

    wb = load_workbook(template_path)

    # Sheet 1

    ws1 = wb[wb.sheetnames[0]]

    for i, value in enumerate(grid_purchase, start=2):
        ws1[f"B{i}"] = float(value)

    # total cost
    ws1["D147"] = float(total_cost)

    # Sheet 2

    if len(wb.sheetnames) > 1:

        ws2 = wb[wb.sheetnames[1]]

        if charge is not None and discharge is not None:

            charge = np.asarray(charge)
            discharge = np.asarray(discharge)

            # 24 intervals = 4 hours
            for block in range(6):

                s = block * 24
                e = s + 24

                ws2[f"B{block+2}"] = float(charge[s:e].sum())
                ws2[f"C{block+2}"] = float(discharge[s:e].sum())

        if battery_energy is not None:

            ws2["E2"] = float(battery_energy[0])
            ws2["E3"] = float(battery_energy[-1])

    wb.save(output_path)
    print(f"结果已导出：{output_path}")