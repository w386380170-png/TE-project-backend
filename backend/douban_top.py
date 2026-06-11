def get_douban_top100():
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

            import re
            # 匹配末尾的 "1994 / 美国 / 剧情" 格式
            pattern_year_area_genre = r"(\d{4} / .+)$"
            match = re.search(pattern_year_area_genre, info_block)

            if match:
                year_area_genre = match.group(1)
                # 前面纯导演主演文本
                director_actor_text = info_block.replace(year_area_genre, "").strip()
                # 拆分年份、国家、类型
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