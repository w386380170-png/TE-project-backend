import pymysql

class MySQLHelper:
    def __init__(self, host, user, password, database):
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.conn = None
        self.cursor = None

    def connect(self):
        """连接数据库"""
        self.conn = pymysql.connect(
            host=self.host,
            user=self.user,
            password=self.password,
            database=self.database,
            charset='utf8mb4'
        )
        self.cursor = self.conn.cursor()

    def execute(self, sql, params=None):
        """执行增删改操作"""
        try:
            self.connect()
            if params:
                self.cursor.execute(sql, params)
            else:
                self.cursor.execute(sql)
            self.conn.commit()
            return True
        except Exception as e:
            print(f"操作失败: {e}")
            self.conn.rollback()
            return False
        finally:
            self.close()