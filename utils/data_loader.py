
from pathlib import Path
import pandas as pd


class DataLoader:
    def __init__(self, data_folder: Path):
        self.data_folder = Path(data_folder)

    def clean_columns(self, df: pd.DataFrame):
        df.columns = (
            df.columns.astype(str)
            .str.replace("\n", "", regex=False)
            .str.replace(" ", "", regex=False)
            .str.strip()
        )
        return df

    # -------------------------------------------------
    # Question 1
    # -------------------------------------------------
    def load_attachment1(self):
        file = self.data_folder / "附件1.xlsx"
        df = pd.read_excel(file)
        return self.clean_columns(df)

    # -------------------------------------------------
    # Question 2
    # -------------------------------------------------
    def load_attachment2(self):
        """
        Read the official Attachment 2.

        Returns
        -------
        dict
            {
                "dates": Series,
                "load": DataFrame(365×144),
                "pv": DataFrame(365×144)
            }
        """

        file = self.data_folder / "附件2.xlsx"

        load_sheet = pd.read_excel(
            file,
            sheet_name="小区负载"
        )

        pv_sheet = pd.read_excel(
            file,
            sheet_name="光伏发电实际功率"
        )

        load_sheet = self.clean_columns(load_sheet)
        pv_sheet = self.clean_columns(pv_sheet)

        dates = pd.to_datetime(
            load_sheet.iloc[:, 0]
        )

        # Only keep the 144 scheduling intervals
        # Ignore the last "0:00+1" column.

        load = load_sheet.iloc[:, 1:145].astype(float)
        pv = pv_sheet.iloc[:, 1:145].astype(float)

        return {
            "dates": dates,
            "load": load,
            "pv": pv,
        }

    # -------------------------------------------------
    # Daily iterator
    # -------------------------------------------------
    def split_into_days(self, attachment2):

        days = []

        dates = attachment2["dates"]
        load = attachment2["load"]
        pv = attachment2["pv"]

        for i in range(len(dates)):

            days.append({
                "date": dates.iloc[i],
                "load": load.iloc[i].to_numpy(float),
                "pv": pv.iloc[i].to_numpy(float),
            })

        return days