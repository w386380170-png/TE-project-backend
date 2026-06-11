import requests
import time
import re
import json
from MySQLHelper import MySQLHelper

# 数据库实例
db = MySQLHelper()

def create_table_baidu_hot():
    """创建百度热搜表 + 清空历史旧数据"""
    sql = """
          CREATE TABLE IF NOT EXISTS baidu_hot (
                                                   id INT AUTO_INCREMENT PRIMARY KEY COMMENT '自增主键',
                                                   hot_title VARCHAR(512) NOT NULL COMMENT '热搜标题',
              hot_score VARCHAR(128) COMMENT '热搜热度指数',
              hot_url VARCHAR(1024) COMMENT '热搜详情链接',
              create_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
              ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4; \
          """
    db.exec_sql(sql)
    # 清空表，保证每次都是最新数据
    db.exec_sql("TRUNCATE TABLE baidu_hot;")
    print("百度热搜表校验完成，已清空旧数据")

def get_baidu_hot():
    """爬取百度实时热搜前10条，修复乱码+网络异常"""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0 Safari/537.36",
        "Referer": "https://top.baidu.com/"
    }
    url = "https://top.baidu.com/board?tab=realtime"
    data = []

    # 增加请求重试机制
    try:
        resp = requests.get(url, headers=headers, timeout=15)
        resp.raise_for_status()
        resp.encoding = "utf-8"
    except requests.exceptions.RequestException as e:
        print(f"百度热搜请求失败：{e}")
        return data

    # 正则提取关键词、热度、链接
    title_list = re.findall(r'"word":"(.*?)"', resp.text)
    score_list = re.findall(r'"hotScore":"(.*?)"', resp.text)
    url_list = re.findall(r'"url":"(.*?)"', resp.text)

    # 取最小长度，防止列表长度不一致报错
    limit = min(10, len(title_list), len(score_list), len(url_list))
    if limit == 0:
        print("⚠未抓取到热搜数据")
        return data

    for i in range(limit):
        raw_title = title_list[i]
        # 多层解码兜底，彻底解决中文乱码
        try:
            # 标准JSON转义解码
            title = json.loads(f'"{raw_title}"')
        except (json.JSONDecodeError, UnicodeError):
            # 备用解码方案
            try:
                title = raw_title.encode("utf-8").decode("unicode_escape")
            except:
                title = raw_title

        score = score_list[i].strip()
        link = url_list[i].strip()
        data.append((title, score, link))

    print(f"成功抓取百度热搜前 {len(data)} 条")
    return data

def save_to_db(data_list):
    """批量插入热搜数据到数据库"""
    if not data_list:
        print("⚠无热搜数据，跳过入库")
        return

    insert_sql = """
                 INSERT INTO baidu_hot (hot_title, hot_score, hot_url)
                 VALUES (%s, %s, %s) \
                 """
    rows = db.batch_insert(insert_sql, data_list)
    print(f"百度热搜入库完成，共插入 {rows} 条")

# 本地单独测试
if __name__ == "__main__":
    create_table_baidu_hot()
    hot_data = get_baidu_hot()
    save_to_db(hot_data)
    print("\n=== 热搜前3条预览 ===")
    for item in hot_data[:3]:
        print(item)