from MySQLHelper import MySQLHelper
from baidu_hot import get_baidu_hot, create_table, save_to_db

# 百度热搜爬虫测试
def test_week2():
    print("\n===== 第二周：百度热搜爬虫 =====")

    # 强制重新连接，保证稳定
    db = MySQLHelper()
    db.connect()
    db.close()

    create_table()    # 创建表
    data = get_baidu_hot()  # 爬数据
    save_to_db(data)       # 存数据库

    print("✅ 爬取成功！热搜前 3 条：")
    for i in range(min(3, len(data))):
        print(data[i])

if __name__ == "__main__":
    test_week2()