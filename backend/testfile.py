# test.py
from main import MySQLHelper

# 数据库配置（改成你自己的）
db = MySQLHelper(
    host="localhost",
    user="root",
    password="你的MySQL密码",
    database="student_db"
)

db.execute("INSERT INTO student (name, height) VALUES (%s, %s)", ("测试学生", 172.50))
students = db.query("SELECT * FROM student")
print("所有学生数据：")
for s in students:
    print(s)