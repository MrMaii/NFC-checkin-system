from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import sqlite3
from datetime import datetime

app = Flask(__name__)
CORS(app)  # 必须允许跨域，否则网页无法发送 POST 请求

# ------------------ 基础配置（部署到公网服务器时使用） ------------------
# 1. 数据库文件路径：强制使用“与 app.py 同目录”的 dormitory.db，避免因为启动目录不同而读到另一份空库
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "dormitory.db")

# 2. 硬件端 / 注册端 调用的 API 密钥
API_KEY = "THOMAS_2026"


def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def check_api_key(req: request) -> bool:
    """简单的 Header 鉴权，用于树莓派等设备访问后端。"""
    key = req.headers.get("X-API-KEY")
    return key == API_KEY


@app.route("/update", methods=["POST"])
def update_status():
    """
    前端网页 / 硬件统一更新接口（主要给网页拖拽用）
    Payload: {"name": "测试一", "status": 1}
    """
    data = request.json or {}
    name = data.get("name")
    status = data.get("status")

    if name is None or status is None:
        return jsonify({"error": "name 或 status 不能为空"}), 400

    # 授时中心：无论谁发起的更新，都以服务器时间为准
    server_time = datetime.now().strftime("%H:%M:%S")

    try:
        conn = get_db_connection()
        # 更新数据库
        conn.execute(
            "UPDATE students SET status = ?, last_update = ? WHERE name = ?",
            (status, server_time, name),
        )
        conn.commit()
        conn.close()

        print(
            f">>> [同步成功] 来源: 终端/网页 | 用户: {name} | 新状态: {status} | 时间: {server_time}"
        )
        return jsonify({"message": "success", "time": server_time}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/scan", methods=["POST"])
def scan_by_uid():
    """
    树莓派 / 读卡器 专用接口：
    Payload: {"uid": "FF FF FF FF"}
    根据 UID 在服务器端数据库中查找学生并翻转 status，同时更新时间。
    """
    if not check_api_key(request):
        return jsonify({"error": "unauthorized"}), 401

    data = request.json or {}
    uid = data.get("uid")
    if not uid:
        return jsonify({"error": "uid 不能为空"}), 400

    server_time = datetime.now().strftime("%H:%M:%S")

    try:
        conn = get_db_connection()
        cur = conn.cursor()

        # 查找学生
        cur.execute("SELECT id, name, status FROM students WHERE uid = ?", (uid,))
        row = cur.fetchone()

        if not row:
            conn.close()
            print(f"!!! [未知卡片] UID: {uid} 未在服务器数据库中登记")
            return jsonify({"error": "unknown uid"}), 404

        student_id, name, current_status = row
        new_status = 1 if current_status == 0 else 0

        # 更新数据库
        cur.execute(
            "UPDATE students SET status = ?, last_update = ? WHERE id = ?",
            (new_status, server_time, student_id),
        )
        conn.commit()
        conn.close()

        action_text = "进入校内" if new_status == 1 else "离开校外"
        print(
            f">>> [硬件端刷卡同步] 学生: {name} | 动作: {action_text} | UID: {uid} | 时间: {server_time}"
        )

        return (
            jsonify(
                {
                    "message": "success",
                    "name": name,
                    "status": new_status,
                    "time": server_time,
                }
            ),
            200,
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/register_student", methods=["POST"])
def register_student():
    """
    树莓派 / 终端 注册脚本使用：
    Payload: {"name": "...", "uid": "...", "room": "...", "email": "..."}
    """
    if not check_api_key(request):
        return jsonify({"error": "unauthorized"}), 401

    data = request.json or {}
    name = data.get("name")
    uid = data.get("uid")
    room = data.get("room")
    email = data.get("email")

    if not all([name, uid, room, email]):
        return jsonify({"error": "缺少必要字段"}), 400

    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO students (name, uid, room, email, status) VALUES (?, ?, ?, ?, 0)",
            (name, uid, room, email),
        )
        conn.commit()
        conn.close()
        print(
            f">>> [新学生注册] 姓名: {name} | UID: {uid} | 房间: {room} | 邮箱: {email}"
        )
        return jsonify({"message": "registered"}), 201
    except sqlite3.IntegrityError:
        # uid 唯一约束
        return jsonify({"error": "该 UID 已存在，请勿重复注册"}), 409
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/get_status", methods=["GET"])
def get_all_status():
    conn = get_db_connection()
    students = conn.execute("SELECT * FROM students").fetchall()
    conn.close()
    return jsonify({s["name"]: dict(s) for s in students})


if __name__ == "__main__":
    # 部署到服务器时建议用 gunicorn/uwsgi 等来启动，这里仅用于本地调试
    app.run(host="0.0.0.0", port=5000)