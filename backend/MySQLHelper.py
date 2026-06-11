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
        if self.conn is None:
            return False
        try:
            self.conn.ping(reconnect=False)
            return self.conn.open
        except pymysql.err.InterfaceError:
            self.conn = None
            self.cursor = None
            return False

    def connect(self):
        try:
            self.conn = pymysql.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database,
                port=self.port,
                charset="utf8mb4",
                autocommit=False
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
        self.cursor = None
        self.conn = None

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
            print(f"SQL执行失败：{sql} 错误：{e}")
            return 0

    # 新增缺失的批量插入方法
    def batch_insert(self, sql, data_list):
        if not self.is_connected():
            self.connect()
        if not self.is_connected():
            print("无法批量插入：数据库未连接")
            return 0
        try:
            self.cursor.executemany(sql, data_list)
            self.conn.commit()
            return self.cursor.rowcount
        except Exception as e:
            if self.conn:
                self.conn.rollback()
            print(f"批量插入失败：{sql} 错误：{e}")
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
            print(f"SQL查询失败：{sql} 错误：{e}")
            return []