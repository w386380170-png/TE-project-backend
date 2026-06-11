import requests
import time
import re
import json

from MySQLHelper import MySQLHelper

# 数据库实例
db = MySQLHelper()

def create_table_baidu_hot():
    """创建百度热搜数据表，不存在则新建"""
    sql = """
          CREATE TABLE IF NOT EXISTS baidu_hot (
                                                   id INT AUTO_INCREMENT PRIMARY KEY COMMENT '自增主键',
                                                   hot_title VARCHAR(512) NOT NULL COMMENT '热搜标题',
              hot_score VARCHAR(128) COMMENT '热搜热度指数',
              hot_url VARCHAR(1024) COMMENT '热搜详情链接',
              create_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '爬取时间'
              ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4; \
          """
    db.exec_sql(sql)
    print("✅ 百度热搜表校验/创建完成")

def get_baidu_hot():
    """爬取百度热搜前10条，返回元组列表[(标题,热度,链接),...]"""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"
    }
    url = "https://top.baidu.com/board?tab=realtime"
    resp = requests.get(url, headers=headers, timeout=10)
    resp.encoding = "utf-8"

    # 正则提取
    title_list = re.findall(r'"word":"(.*?)"', resp.text)
    score_list = re.findall(r'"hotScore":"(.*?)"', resp.text)
    url_list = re.findall(r'"url":"(.*?)"', resp.text)

    data = []
    limit = min(10, len(title_list), len(score_list), len(url_list))
    for i in range(limit):
        raw_title = title_list[i]
        # 标准Unicode转义解码，兜底捕获异常防止程序中断
        try:
            title = json.loads(f'"{raw_title}"')
        except json.JSONDecodeError:
            title = raw_title.encode("utf-8").decode("unicode_escape")

        score = score_list[i]
        link = url_list[i]
        data.append((title, score, link))

    print(f"✅ 成功抓取百度热搜前{len(data)}条")
    return data

def save_to_db(data_list):
    """批量将热搜数据存入数据库"""
    if not data_list:
        print("⚠️ 无热搜数据，跳过入库")
        return
    insert_sql = """
                 INSERT INTO baidu_hot (hot_title, hot_score, hot_url)
                 VALUES (%s, %s, %s) \
                 """
    rows = db.batch_insert(insert_sql, data_list)
    print(f"✅ 百度热搜入库完成，共插入{rows}条")

# 本地测试入口
if __name__ == "__main__":
    create_table_baidu_hot()
    hot_data = get_baidu_hot()
    save_to_db(hot_data)
    print("=== 热搜前3条预览 ===")
    for item in hot_data[:3]:
        print(item)