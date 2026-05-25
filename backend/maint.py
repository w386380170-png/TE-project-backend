from fastapi import FastAPI
from database import engine, Base
from routers import auth

# 创建所有数据库表（如果不存在）
Base.metadata.create_all(bind=engine)
app = FastAPI(title="AI Agent 管理系统")

app.include_router(auth.router)

@app.get("/docs")
def home():
    return {"message": "项目启动成功！✅"}

