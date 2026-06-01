import pymysql
from pymysql.cursors import DictCursor

class MySQLHelper:
    def __init__(self, host="localhost", user="root", pwd="", db="studentinf", port=3306):
        self.host = host
        self.user = user
        self.password = pwd
        self.database = db
        self.port = port
        self.conn = None
        self.cursor = None

    def is_connected(self):
        return self.conn is not None and self.conn.open

    def connect(self):
        try:
            self.conn = pymysql.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database,
                port=self.port,
                charset="utf8mb4"
            )
            self.cursor = self.conn.cursor(DictCursor)
            print("✅ 数据库连接成功")
        except Exception as e:
            print(f"数据库连接失败：{e}")
            self.conn = None
            self.cursor = None

    def close(self):
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()

    def exec_sql(self, sql, params=None):
        if not self.is_connected():
            self.connect()
        if not self.is_connected():
            print("无法执行SQL：数据库未连接")
            return 0

        try:
            self.cursor.execute(sql, params or ())
            self.conn.commit()
            return self.cursor.rowcount
        except Exception as e:
            if self.conn:
                self.conn.rollback()
            print(f"执行失败：{e}")
            return 0

    def query_sql(self, sql, params=None):
        if not self.is_connected():
            self.connect()
        if not self.is_connected():
            print("无法查询SQL：数据库未连接")
            return []

        try:
            self.cursor.execute(sql, params or ())
            return self.cursor.fetchall()
        except Exception as e:
            print(f"查询失败：{e}")
            return []