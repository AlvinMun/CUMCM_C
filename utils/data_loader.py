
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

    # Question 1
    def load_attachment1(self):
        file = self.data_folder / "附件1.xlsx"
        df = pd.read_excel(file)
        return self.clean_columns(df)

    # Question 2
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

    def load_attachment3(self):
        """
        Read Attachment 3 (PV forecast).

        Returns:
            list of 365 dictionaries.

        Each day contains:
            {
                "date": datetime,
                "forecast": {
                    "0:00": np.array(144),
                    "6:00": np.array(144),
                    "12:00": np.array(144),
                    "18:00": np.array(144),
                }
            }
        """

        import pandas as pd
        import numpy as np

        file = self.data_folder / "附件3.xlsx"

        df = pd.read_excel(file)

        result = []

        i = 0
        while i < len(df):

            date = pd.to_datetime(df.iloc[i, 0])

            forecasts = {}

            for j in range(4):

                row = df.iloc[i + j]

                release = str(row["预报时刻"])

                hourly = row.iloc[2:26].to_numpy(dtype=float)

                # Expand 24 hourly values → 144 ten-minute values
                ten_min = np.repeat(hourly, 6)

                forecasts[release] = ten_min

            result.append({
                "date": date,
                "forecast": forecasts,
            })

            i += 4

        return result

    def load_attachment4(self):
        """
        Load Attachment 4 (全年波动电价).

        Returns
        -------
        list[dict]
            Each element represents one day:
            {
                "date": Timestamp,
                "price": ndarray(144)
            }
        """

        file_path = self.data_folder / "附件4.xlsx"

        df = pd.read_excel(file_path)

        date_col = df.columns[0]

        df[date_col] = pd.to_datetime(df[date_col])

        price_days = []

        for _, row in df.iterrows():

            price_days.append({
                "date": row[date_col],
                "price": row.iloc[1:].to_numpy(dtype=float),
            })

        return price_days

    # Daily iterator
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