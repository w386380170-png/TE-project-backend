import requests
import time
import re
from bs4 import BeautifulSoup
from MySQLHelper import MySQLHelper

# 数据库实例
db = MySQLHelper()

def create_table_douban_movie():
    """创建豆瓣电影数据表 + 清空旧数据"""
    sql = """
          CREATE TABLE IF NOT EXISTS douban_movies (
                                                       id INT AUTO_INCREMENT PRIMARY KEY COMMENT '主键',
                                                       movie_name VARCHAR(512) NOT NULL COMMENT '电影名称',
              score DECIMAL(3,1) COMMENT '评分',
              director VARCHAR(256) COMMENT '导演',
              actors TEXT COMMENT '主演',
              release_year INT COMMENT '上映年份',
              movie_type VARCHAR(256) COMMENT '影片类型',
              country VARCHAR(128) COMMENT '制片国家',
              summary TEXT COMMENT '简介',
              movie_url VARCHAR(1024) COMMENT '豆瓣链接',
              crawl_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
              ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4; \
          """
    db.exec_sql(sql)
    db.exec_sql("TRUNCATE TABLE douban_movies;")
    print("豆瓣电影表校验完成，已清空旧数据")

def get_douban_top100():
    """爬取豆瓣Top250前100部电影，高容错解析，解决字段错位"""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"
    }
    all_movie_data = []
    page_offsets = [0, 25, 50, 75]

    for offset in page_offsets:
        url = f"https://movie.douban.com/top250?start={offset}"
        try:
            resp = requests.get(url, headers=headers, timeout=12)
            resp.raise_for_status()
        except Exception as e:
            print(f"第{int(offset/25)+1}页请求失败：{e}")
            continue

        soup = BeautifulSoup(resp.text, "html.parser")
        items = soup.select(".item")

        for item in items:
            # 基础字段解析
            title = item.select_one(".title").get_text(strip=True) if item.select_one(".title") else ""
            score_text = item.select_one(".rating_num").get_text(strip=True) if item.select_one(".rating_num") else "0"
            score = float(score_text)
            detail_url = item.select_one(".pic a")["href"] if item.select_one(".pic a") else ""
            info_block = item.select_one(".bd p").get_text(strip=True) if item.select_one(".bd p") else ""

            year = ""
            country = ""
            genre = ""
            director = ""
            actor = ""

            # 正则匹配尾部 年份 / 地区 / 类型
            pattern = r"(\d{4})\s*/\s*(.+?)\s*/\s*(.+)$"
            match = re.search(pattern, info_block)
            if match:
                year = match.group(1).strip()
                country = match.group(2).strip()
                genre = match.group(3).strip()
                # 截取前面 导演+主演 部分
                director_actor_text = info_block[:match.start()].strip()
            else:
                director_actor_text = info_block

            # 拆分导演、主演
            if "主演:" in director_actor_text:
                dir_part, act_part = director_actor_text.split("主演:", 1)
                director = dir_part.replace("导演:", "").strip()
                actor = act_part.strip()
            elif "导演:" in director_actor_text:
                director = director_actor_text.replace("导演:", "").strip()
                actor = ""
            else:
                director = director_actor_text.strip()
                actor = ""

            # 简介兜底
            summary = item.select_one(".inq").get_text(strip=True) if item.select_one(".inq") else ""

            # 年份类型转换，非数字置为None
            year_num = int(year) if year.isdigit() else None

            # 组装行数据
            movie_row = (
                title, score, director, actor,
                year_num, genre, country, summary, detail_url
            )
            all_movie_data.append(movie_row)

        time.sleep(2)
        print(f"已完成第 {int(offset/25)+1} 页抓取")

    result = all_movie_data[:100]
    print(f"全部抓取完成，总计{len(result)}部电影")
    return result

def save_douban_to_db(movie_list):
    """批量将电影数据存入数据库"""
    if not movie_list:
        print("⚠无电影数据，跳过入库")
        return
    insert_sql = """
                 INSERT INTO douban_movies
                 (movie_name, score, director, actors, release_year, movie_type, country, summary, movie_url)
                 VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s) \
                 """
    insert_count = db.batch_insert(insert_sql, movie_list)
    print(f"豆瓣电影入库完成，共插入{insert_count}条")

# 本地测试入口
if __name__ == "__main__":
    create_table_douban_movie()
    movie_data = get_douban_top100()
    save_douban_to_db(movie_data)