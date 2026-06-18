from fastapi import APIRouter
from pydantic import BaseModel
from MySQLHelper import MySQLHelper

router = APIRouter(prefix="/api/auth", tags=["用户登录注册"])

db = MySQLHelper(pwd="", db="studentinf")


class UserBody(BaseModel):
    username: str
    password: str


def create_user_table():
    sql = """
    CREATE TABLE IF NOT EXISTS users (
        id INT AUTO_INCREMENT PRIMARY KEY,
        username VARCHAR(50) NOT NULL UNIQUE,
        password VARCHAR(100) NOT NULL,
        create_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    """
    db.exec_sql(sql)


@router.post("/register")
def register(user: UserBody):
    create_user_table()

    exist = db.query_sql(
        "SELECT id FROM users WHERE username=%s",
        (user.username,)
    )
    if exist:
        return {"code": 400, "msg": "用户名已存在"}

    db.exec_sql(
        "INSERT INTO users (username, password) VALUES (%s, %s)",
        (user.username, user.password)
    )
    return {"code": 200, "msg": "注册成功"}


@router.post("/login")
def login(user: UserBody):
    create_user_table()

    result = db.query_sql(
        "SELECT id, username FROM users WHERE username=%s AND password=%s",
        (user.username, user.password)
    )
    if result:
        return {"code": 200, "msg": "登录成功", "user": result[0]}

    return {"code": 401, "msg": "用户名或密码错误"}