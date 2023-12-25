import os
import sqlite3


class SqliteClient:
    def __init__(self):
        self.conn = sqlite3.connect(os.environ["DB_FILE"])
        self.cursor = self.conn.cursor()
        self.execute("PRAGMA foreign_keys = ON;")

    def execute(self, query, params=None):
        if params:
            self.cursor.execute(query, params)
        else:
            self.cursor.execute(query)

    def insert(self, table, values):
        self.execute(
            f"insert into {table} values ({','.join(['?'] * len(values))})", values
        )
        self.commit()
        return self.cursor.lastrowid

    def fetchall(self):
        return self.cursor.fetchall()

    def fetchone(self):
        return self.cursor.fetchone()

    def commit(self):
        self.conn.commit()

    def close(self):
        self.conn.close()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()
