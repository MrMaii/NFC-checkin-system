from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime

app = Flask(__name__)

# --- 核心配置 ---
# 1. 开启 CORS：这是为了让你的精美网页（React）能从浏览器里合法地拿到这个后端的数据
CORS(app)

# 2. 安全暗号：确保只有你的树莓派/电脑能修改数据
API_KEY = "THOMAS_2026"

# 3. 数据存储（临时存在内存里，重启程序会重置，适合开发阶段）
# 以后可以升级为连接云端数据库
status_store = {
    "name": "Thomas",
    "status": 0,           # 0: 离校, 1: 在校
    "last_update": "N/A",  # 最后更新时间
    "message": "系统已启动，等待刷卡..."
}

# --- 接口 A：给硬件端（read_card.py）投递数据 ---
@app.route('/update', methods=['POST'])
def update_attendance():
    global status_store
    
    # 安全检查：看看有没有带暗号
    incoming_key = request.headers.get("X-API-KEY")
    if incoming_key != API_KEY:
        return jsonify({"error": "Unauthorized: 密钥错误或缺失"}), 403

    # 解析发送过来的 JSON 数据
    data = request.json
    if not data:
        return jsonify({"error": "无效的数据包"}), 400

    # 更新状态
    status_store["status"] = data.get("status", 0)
    # 重要：由后端生成权威的“服务器时间戳”
    status_store["last_update"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    status_store["message"] = f"已于 {status_store['last_update']} 更新状态"

    print(f">>> [收到推送] {status_store['name']} 当前状态: {status_store['status']}")
    return jsonify({"message": "同步成功", "server_time": status_store["last_update"]}), 200

# --- 接口 B：给网页端（React）读取数据 ---
@app.route('/get_status', methods=['GET'])
def get_current_status():
    # 网页端只需要直接访问这个接口就能拿到最新的 JSON 数据
    return jsonify(status_store)

# --- 启动服务器 ---
if __name__ == '__main__':
    # 运行在本地 5000 端口
    print("========================================")
    print("   Thomas NFC 签到系统 - 云端后端已启动   ")
    print("   接口 A (POST): /update              ")
    print("   接口 B (GET):  /get_status           ")
    print("========================================")
    app.run(host='0.0.0.0', port=5000, debug=True)