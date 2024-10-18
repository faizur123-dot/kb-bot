import pandas as pd
from constants import constants
import psycopg2
import os
from utils.singleton_class import SingletonMeta


class DatabaseConnection(metaclass=SingletonMeta):

    def __init__(self):
        self.connection = None
        self.host = os.getenv("POSTGRES_RDS_HOST")
        self.database = os.getenv("POSTGRES_RDS_DATABASE")
        self.password = os.getenv("POSTGRES_RDS_PASSWORD")
        self.port = constants.POSTGRES_PORT
        self.user = constants.POSTGRES_USER

    def __enter__(self):
        self.open_connection()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if not exc_type:
            self.connection.commit()
        else:
            self.connection.rollback()
        self.connection.autocommit = True
        self.close_connection()

    def open_connection(self):
        try:
            self.connection = psycopg2.connect(
                host=self.host,
                port=self.port,
                database=self.database,
                user=self.user,
                password=self.password,
            )
            self.connection.autocommit = False
        except psycopg2.Error as e:
            raise e

    def close_connection(self):
        if self.connection is not None:
            self.connection.close()

    def get_rows_from_table(self, tablename, *columns, where_condition_dict):
        connection = psycopg2.connect(
            host=self.host,
            port=self.port,
            database=self.database,
            user=self.user,
            password=self.password,
        )
        cursor = connection.cursor()
        query = f"SELECT {', '.join(columns)} FROM {tablename}"

        conditions = []
        for key, values in where_condition_dict.items():
            if isinstance(values, str):
                values = [values]
            elif isinstance(values, int):
                values = [str(values)]
            elif isinstance(values, pd.Series):
                values = values.tolist()
            else:
                values = [str(value) for value in values]
            values = [f"'{value}'" for value in values]
            conditions.append(f"{key} IN ({', '.join(values)})")

        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        cursor.execute(query)
        data = cursor.fetchall()
        df = pd.DataFrame(data, columns=columns)

        cursor.close()
        connection.close()

        return df

    def update_row_into_table(self, tablename, data, where_condition_dict):
        connection = psycopg2.connect(
            host=self.host,
            port=self.port,
            database=self.database,
            user=self.user,
            password=self.password,
        )
        cursor = connection.cursor()
        query = f"UPDATE {tablename} SET "

        updates = []
        for key, value in data.items():
            updates.append(f"{key} = '{value}'")

        query += ", ".join(updates)

        conditions = []
        for key, values in where_condition_dict.items():
            if isinstance(values, str):
                values = [values]
            elif isinstance(values, int):
                values = [str(values)]
            elif isinstance(values, pd.Series):
                values = values.tolist()
            else:
                values = [str(value) for value in values]
            values = [f"'{value}'" for value in values]
            conditions.append(f"{key} IN ({', '.join(values)})")

        if conditions:
            query += " WHERE " + " AND ".join(conditions)

        cursor.execute(query)
        connection.commit()

        cursor.close()
        connection.close()
        return

    def insert_row_into_table(self, table_name: str, data):
        conn = psycopg2.connect(
            host=self.host,
            port=self.port,
            database=self.database,
            user=self.user,
            password=self.password,
        )
        cursor = conn.cursor()

        for row in data:
            column_names = ', '.join(row.keys())
            values = tuple(row.values())
            query = f"INSERT INTO {table_name} ({column_names}) VALUES {values}"
            cursor.execute(query)

        conn.commit()

        cursor.close()
        conn.close()

    def upsert_row_into_table(self, table_name: str, data, conflict_columns: list):
        conn = psycopg2.connect(
            host=self.host,
            port=self.port,
            database=self.database,
            user=self.user,
            password=self.password,
        )
        cursor = conn.cursor()

        for row in data:
            column_names = ', '.join(row.keys())
            values = tuple(row.values())
            conflict_clause = ', '.join(conflict_columns)
            update_clause = ', '.join([f"{col} = EXCLUDED.{col}" for col in row.keys()])

            query = f"""
            INSERT INTO {table_name} ({column_names}) 
            VALUES {values}
            ON CONFLICT ({conflict_clause}) 
            DO UPDATE SET {update_clause}
            """
            cursor.execute(query)

        conn.commit()

        cursor.close()
        conn.close()
