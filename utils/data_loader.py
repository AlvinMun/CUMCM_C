
from pathlib import Path
import pandas as pd


class DataLoader:
    """
    Read all official CUMCM attachments.
    """

    def __init__(self, data_folder: Path):
        self.data_folder = Path(data_folder)

    def load_attachment1(self):
        return pd.read_excel(
            self.data_folder / "附件1.xlsx"
        )

    def load_attachment2(self):
        return pd.read_excel(
            self.data_folder / "附件2.xlsx"
        )

    def load_attachment3(self):
        return pd.read_excel(
            self.data_folder / "附件3.xlsx"
        )

    def load_attachment4(self):
        return pd.read_excel(
            self.data_folder / "附件4.xlsx"
        )

    @staticmethod
    def clean_columns(df):
        df = df.copy()
        df.columns = [
            str(col).strip()
            for col in df.columns
        ]
        return df