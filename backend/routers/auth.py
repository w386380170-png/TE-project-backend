from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter(prefix="/api/auth", tags=["用户认证"])

# 模拟数据库（暂时用列表存用户）
fake_users_db = []

# 用户注册请求体格式
class UserCreate(BaseModel):
    username: str
    password: str

# 注册接口
@router.post("/register")
def register(user: UserCreate):
    # 检查用户名是否已存在
    for u in fake_users_db:
        if u["username"] == user.username:
            raise HTTPException(status_code=400, detail="用户名已存在")

    # 把用户加入“数据库”
    fake_users_db.append({
        "username": user.username,
        "password": user.password  # 真实项目要加密
    })

    return {"message": "注册成功！", "username": user.username}


# 登录接口
@router.post("/login")
def login(user: UserCreate):
    for u in fake_users_db:
        if u["username"] == user.username and u["password"] == user.password:
            return {"message": "登录成功！", "username": user.username}

    raise HTTPException(status_code=401, detail="用户名或密码错误")


# 功能1
# 功能2
