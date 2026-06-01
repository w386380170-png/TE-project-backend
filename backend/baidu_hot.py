import requests
from bs4 import BeautifulSoup
from MySQLHelper import MySQLHelper

# 爬取百度热搜 Top10
def get_baidu_hot():
    url = "https://top.baidu.com/board?tab=realtime"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")

    hot_list = []
    items = soup.select(".item-wrap_2oCLZ")

    for i, item in enumerate(items[:10], 1):
        title = item.select_one(".c-single-text-ellipsis").text.strip()
        hot = item.select_one(".hot-index_1Bl1a").text.strip()
        hot_list.append([i, title, hot])

    return hot_list

# 创建数据表
def create_table():
    db = MySQLHelper()
    sql = """
          CREATE TABLE IF NOT EXISTS baidu_hot (
                                                   id INT PRIMARY KEY AUTO_INCREMENT,
                                                   rank INT,
                                                   title VARCHAR(255),
              hot VARCHAR(50),
              create_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
              ) \
          """
    db.exec_sql(sql)
    print("✅ baidu_hot 表创建成功")
    db.close()

# 保存到数据库
def save_to_db(hot_list):
    db = MySQLHelper()
    for item in hot_list:
        sql = "INSERT INTO baidu_hot (rank, title, hot) VALUES (%s, %s, %s)"
        db.exec_sql(sql, (item[0], item[1], item[2]))
    print("✅ 百度热搜数据入库完成")
    db.close()