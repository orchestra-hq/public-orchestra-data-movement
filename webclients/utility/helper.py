import pandas as pd


class Helper:
    def __init__(self):
        pass

    def flatten_list_of_list(self, list__: list):
        return [item for sublist in list__ for item in sublist]

    def make_df_from_list(self, list_: list, columns: list):
        df = pd.DataFrame(list_, columns=columns)
        return df