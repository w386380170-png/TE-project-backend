import requests
import time
import re
from bs4 import BeautifulSoup
from MySQLHelper import MySQLHelper

# 数据库实例
db = MySQLHelper()

def create_table_douban_movie():
    """创建豆瓣电影数据表 + 清空旧错位数据"""
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
    # 清空之前错位的脏数据，保证每次爬取都是最新的100条
    db.exec_sql("TRUNCATE TABLE douban_movies;")
    print("✅ 豆瓣电影表校验完成，已清空旧数据")

def get_douban_top100():
    """爬取豆瓣Top250前100部电影，修复字段错位问题"""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"
    }
    all_movie_data = []
    page_offsets = [0, 25, 50, 75]

    for offset in page_offsets:
        url = f"https://movie.douban.com/top250?start={offset}"
        resp = requests.get(url, headers=headers, timeout=12)
        soup = BeautifulSoup(resp.text, "html.parser")
        items = soup.select(".item")

        for item in items:
            title = item.select_one(".title").get_text(strip=True)
            score = float(item.select_one(".rating_num").get_text(strip=True))
            detail_url = item.select_one(".pic a")["href"]
            info_block = item.select_one(".bd p").get_text(strip=True)

            #正则分离导演/主演 和 年份/地区/类型
            pattern_year_area_genre = r"(\d{4} / .+)$"
            match = re.search(pattern_year_area_genre, info_block)

            if match:
                year_area_genre = match.group(1)
                director_actor_text = info_block.replace(year_area_genre, "").strip()
                year, country, genre = year_area_genre.split(" / ")
            else:
                director_actor_text = info_block
                year = ""
                country = ""
                genre = ""

            # 拆分导演、主演
            if "主演:" in director_actor_text:
                director = director_actor_text.split("主演:")[0].replace("导演: ", "").strip()
                actor = director_actor_text.split("主演:")[-1].strip()
            else:
                director = director_actor_text.replace("导演: ", "").strip()
                actor = ""

            # 简介
            summary = item.select_one(".inq").get_text(strip=True) if item.select_one(".inq") else ""

            movie_row = (
                title, score, director, actor,
                int(year) if year.isdigit() else None,
                genre, country, summary, detail_url
            )
            all_movie_data.append(movie_row)
        time.sleep(2)
        print(f"已完成第 {int(offset/25)+1} 页抓取")

    result = all_movie_data[:100]
    print(f"✅ 全部抓取完成，总计{len(result)}部电影")
    return result

def save_douban_to_db(movie_list):
    """批量将电影数据存入数据库"""
    if not movie_list:
        print("⚠️ 无电影数据，跳过入库")
        return
    insert_sql = """
                 INSERT INTO douban_movies
                 (movie_name, score, director, actors, release_year, movie_type, country, summary, movie_url)
                 VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s) \
                 """
    insert_count = db.batch_insert(insert_sql, movie_list)
    print(f"✅ 豆瓣电影入库完成，共插入{insert_count}条")

# 本地测试入口
if __name__ == "__main__":
    create_table_douban_movie()
    movie_data = get_douban_top100()
    save_douban_to_db(movie_data)