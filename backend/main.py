from fastapi import FastAPI,Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
from auth import router as auth_router
# 数据库工具
from MySQLHelper import MySQLHelper
# 百度热搜爬虫
from baidu_hot import get_baidu_hot, create_table_baidu_hot, save_to_db
# 豆瓣电影爬虫
from douban_top import get_douban_top100, create_table_douban_movie, save_douban_to_db

# 初始化服务
app = FastAPI(title="爬虫数据可视化后端API")
app.include_router(auth_router)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
class DemoBody(BaseModel):
    body: str

# 全局数据库实例
db_helper = MySQLHelper(pwd="", db="studentinf")

# 根页面
@app.get("/")
def root():
    return {
        "msg": "爬虫可视化API服务运行正常",
        "接口文档地址": "http://127.0.0.1:8000/docs"
    }

@app.get("/api/demo/get-param")
def demo_get_param(value: str = Query("")):
    return {
        "code": 200,
        "msg": f"参数是 {value}"
    }


@app.post("/api/demo/post-param")
def demo_post_param(data: DemoBody, param: str = Query("")):
    return {
        "code": 200,
        "body_result": f"body中的参数是 {data.body}",
        "param_result": f"param中的参数是 {param}"
    }

# ==================== 百度热搜接口 ====================
@app.get("/api/baidu/hot/crawl")
def crawl_baidu():
    """手动触发爬取百度热搜前10并入库"""
    create_table_baidu_hot()
    data = get_baidu_hot()
    save_to_db(data)
    return {
        "code": 200,
        "msg": "百度热搜Top10爬取入库成功",
        "total": len(data),
        "sample": data[:3]
    }

@app.get("/api/baidu/hot/list")
def get_baidu_list():
    """查询已存储的热搜数据，前端表格展示"""
    res = db_helper.query_sql("SELECT * FROM baidu_hot ORDER BY create_time DESC;")
    return {"code": 200, "data": res}

# ==================== 豆瓣电影接口（Top100可视化） ====================
@app.get("/api/douban/movie/crawl")
def crawl_douban():
    """爬取豆瓣Top100电影入库"""
    create_table_douban_movie()
    movie_data = get_douban_top100()
    save_douban_to_db(movie_data)
    return {
        "code": 200,
        "msg": "豆瓣电影Top100爬取入库成功",
        "total": len(movie_data)
    }

@app.get("/api/douban/movie/list")
def get_douban_list():
    """查询全部100部电影明细"""
    sql = "SELECT * FROM douban_movies ORDER BY score DESC LIMIT 100;"
    data = db_helper.query_sql(sql)
    return {"code": 200, "data": data}

@app.get("/api/douban/stat/score")
def score_stat():
    sql = """
          SELECT
              CASE
                  WHEN score >= 9 THEN '9分及以上'
                  WHEN score >= 8 THEN '8~9分'
                  ELSE '7~8分'
                  END AS score_range,
              COUNT(*) AS movie_count
          FROM douban_movies
          GROUP BY score_range;
          """
    stat = db_helper.query_sql(sql)
    return {"code": 200, "data": stat}

@app.get("/api/douban/stat/country")
def country_stat():
    sql = "SELECT country, COUNT(*) AS movie_count FROM douban_movies GROUP BY country;"
    stat = db_helper.query_sql(sql)
    return {"code": 200, "data": stat}

# 启动服务
if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)