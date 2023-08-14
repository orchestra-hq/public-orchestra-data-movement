import snowflake.connector
from snowflake.connector.errors import Error as SnowflakeError
from webclients.authentication.secretsManager import AWSSecretsManagerService
from pandas import DataFrame
import snowflake.connector.pandas_tools as pdtools
import pandas as pd


class Snowflake:

    secret_keys = [
        "snowflake-db-user",
        "snowflake-db-password",
        "snowflake-database",
        "snowflake-schema",
        "snowflake-warehouse",
        "snowflake-account",
    ]

    base_dict = {
        "messages": None,
        "rowcount": None,
        "sfqid": None,
        "msg": None,
        "errno": None,
        "sqlstate": None,
        "query": None,
        "errno": None,
    }

    def __init__(self, clientguid: str = None):
        kv = AWSSecretsManagerService()
        if clientguid:
            self.secret_keys = [x + f"-{clientguid}" for x in self.secret_keys]
        self.__secrets = kv.get_secrets(self.secret_keys)
        self.__secrets = {
            key.replace(f"-{clientguid}", ""): value
            for key, value in self.__secrets.items()
        }

    def test_connection(self, __secrets: dict):
        try:
            self.return_connection(__secrets)
            return {
                "data": {},
                "internal_status_code": 2,
                "reason": "OK",
                "status_code": 200,
            }
        except Exception as error:
            items = str(error).split(":")
            items = [
                x.lower().replace(" ", "").replace("http", "")
                for x in items
                if "http" in x.lower()
            ]
            for i in items:
                if not i.isdigit():
                    items.remove(i)
            if len(items) == 0:
                status_code = 400
            else:
                status_code = int(items[0])
            return {
                "data": {},
                "internal_status_code": 3,
                "reason": str(error),
                "status_code": status_code,
            }


    def run_command_or_fetch(self, connection, query, base_dict: dict, command=True):
        data = {}
        try:
            results = connection.cursor().execute(query)
            if not command:
                data = results.fetchall()
            error_message = None
            base_dict["messages"] = results.messages
            base_dict["rowcount"] = results.rowcount
            base_dict["sfqid"] = results.sfqid
            status_code = 200
        except SnowflakeError as error:
            error_message = str(error)
            base_dict["msg"] = error.msg
            base_dict["errno"] = error.errno
            base_dict["sqlstate"] = error.sqlstate
            base_dict["sfqid"] = error.sfqid
            base_dict["query"] = error.query
            status_code = 400

        status = connection.get_query_status(base_dict["sfqid"]).name
        return {
            "data": {**data, **{"metdata": base_dict}},
            "status": status,
            "reason": status,
            "status_code": status_code,
            "error_message": error_message,
        }


    def run_fetch(self, connection, query) -> dict:
        base_dict_instance = self.base_dict
        return self.run_command_or_fetch(
            connection, query, base_dict_instance, command=False
        )

    def run_command(self, connection, query) -> dict:
        base_dict_instance = self.base_dict
        return self.run_command_or_fetch(
            connection, query, base_dict_instance, command=True
        )

    def run_query(self, query: str, command: bool = False) -> DataFrame:
        con = self.return_connection(self.__secrets)
        base_dict_instance = self.base_dict
        output = self.run_command_or_fetch(
            con, query, base_dict_instance, command=command
        )
        con.close()
        return output

    def return_connection(self, __secrets: dict = None):
        if not __secrets:
            __secrets = self.__secrets
        return snowflake.connector.connect(
            user=__secrets["snowflake-db-user"],
            password=__secrets["snowflake-db-password"],
            database=__secrets["snowflake-database"],
            schema=__secrets["snowflake-schema"],
            warehouse=__secrets["snowflake-warehouse"],
            account=__secrets["snowflake-account"],
        )

    def create_snowflake_table(self, table_name: str, schema: dict):
        schema_string = [f"{key} {value}" for key,value in schema.items()].join(",")
        query  = f"CREATE OR REPLACE TABLE IF NOT EXISTS {table_name} ({schema_string})"
        connection = self.return_connection()
        self.run_command(connection, query)
        return

    def drop_table(self, table_name: str):
        query  = f"DROP TABLE {table_name}"
        connection = self.return_connection()
        self.run_command(connection, query)
        return 

    def upsert_data(self, target:str, source:str, primary_key:str, schema__: dict):
        columns = [key for key,value in schema__.items()]
        columns.append(primary_key)
        col_string = [f"{x} as {x} "for x in columns].join(",")
        target_string = [f"target.{x} = source.{x}" for x in columns].join(",")
        source_string = [f"source.{x}" for x in columns].join(",")
        col_list = columns.join(",")
        query = f"""MERGE INTO {target} AS target USING (
                    SELECT {col_string} FROM {source} ) AS source
                    ON target.{primary_key} = source.{primary_key}
                    WHEN MATCHED THEN UPDATE SET 
                    {target_string}
                    WHEN NOT MATCHED THEN 
                    INSERT ({col_list})     VALUES ({source_string})"""
        connection = self.return_connection()
        self.run_command(connection, query)
        return 
    
    def write_pandas_to_sf(self, df_, table_name, overwrite = False):
        con_ = snowflake.connector.connect(
            user=self.__secrets["snowflake-db-user"],
            password=self.__secrets["snowflake-db-password"],
            database=self.__secrets["snowflake-database"],
            schema=self.__secrets["snowflake-db-schema"],
            warehouse=self.__secrets["snowflake-warehouse"],
            account=self.__secrets["snowflake-account"],
        )

        try:
            pdtools.write_pandas(table_name=table_name, conn=con_, df=df_, overwrite=overwrite)
        except Exception as e:
            print(e)

        finally:
            con_.close()