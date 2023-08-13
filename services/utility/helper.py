import pandas as pd


class Helper:
    secret_keys = []

    def __init__(self):
        # kv = KeyVaultService("public-api")
        # self.__secrets = kv.get_secrets(self.secret_keys)
        pass

    def flatten_list_of_list(self, list__: list):
        return [item for sublist in list__ for item in sublist]

    def make_df_from_list(self, list_: list, columns: list):
        df = pd.DataFrame(list_, columns=columns)
        return df