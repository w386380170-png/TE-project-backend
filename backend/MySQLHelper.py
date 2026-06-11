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

    def connect(self):
        """每次都创建新连接，不依赖长连接"""
        try:
            # 先关闭旧连接
            if self.conn:
                try:
                    self.conn.close()
                except:
                    pass
            # 创建新连接
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
            return True
        except Exception as e:
            print(f"数据库连接失败：{e}")
            self.conn = None
            self.cursor = None
            return False

    def close(self):
        if self.cursor:
            try:
                self.cursor.close()
            except:
                pass
        if self.conn:
            try:
                self.conn.close()
            except:
                pass
        self.cursor = None
        self.conn = None

    def exec_sql(self, sql, params=None):
        """执行写操作（INSERT/UPDATE/DELETE/TRUNCATE）"""
        # 每次都重新连接
        if not self.connect():
            return 0
        try:
            self.cursor.execute(sql, params or ())
            self.conn.commit()
            affected = self.cursor.rowcount
            self.close()
            return affected
        except Exception as e:
            print(f"SQL执行失败：{sql} 错误：{e}")
            if self.conn:
                self.conn.rollback()
            self.close()
            return 0

    def query_sql(self, sql, params=None):
        """执行查询操作（SELECT）"""
        # 每次都重新连接
        if not self.connect():
            return []
        try:
            self.cursor.execute(sql, params or ())
            result = self.cursor.fetchall()
            self.close()
            return result
        except Exception as e:
            print(f"SQL查询失败：{sql} 错误：{e}")
            self.close()
            return []

    def batch_insert(self, sql, data_list):
        """批量插入"""
        if not self.connect():
            return 0
        try:
            self.cursor.executemany(sql, data_list)
            self.conn.commit()
            affected = self.cursor.rowcount
            self.close()
            return affected
        except Exception as e:
            print(f"批量插入失败：{sql} 错误：{e}")
            if self.conn:
                self.conn.rollback()
            self.close()
            return 0