import sqlite3
class Database:
    def __init__(self,db_path) -> None:
        self.db = sqlite3.connect(db_path)
        def dict_factory(cursor,row):
            dick = {}
            for index, col in enumerate(cursor.description):
                dick[col[0]] = row[index]
            return dick
        self.db.row_factory = dict_factory
        self.cursor = self.db.cursor()
    def exec(self,sql) -> None:
        self.cursor.execute(sql)
        return self.db.commit()
    def find(self,sql) -> dict:
        data = self.cursor.execute(sql)
        return data.fetchone()
    def select(self,sql) -> list:
        data = self.cursor.execute(sql)
        return data.fetchall()