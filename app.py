from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime

app = Flask(__name__)
CORS(app)

# --- 核心配置 ---
API_KEY = "THOMAS_2026"

# --- 多用户花名册 ---
# 现在的存储结构是一个大字典，Key 是学生姓名，Value 是该学生的详细状态
# 初始状态可以是空的，只要有人刷卡，它就会自动长出新内容
students_data = {}

@app.route('/update', methods=['POST'])
def update_status():
    global students_data
    
    # 1. 验证暗号
    incoming_key = request.headers.get("X-API-KEY")
    if incoming_key != API_KEY:
        return jsonify({"error": "Unauthorized"}), 403

    # 2. 获取硬件端传来的数据
    data = request.json
    name = data.get("name")
    status = data.get("status")
    room = data.get("room", "未知房号") # 假设你之后也会传房号

    if not name:
        return jsonify({"error": "缺少姓名"}), 400

    # 3. 动态更新/创建该学生的数据
    # 如果这个学生不在花名册里，Python 会自动为他创建一个新条目
    students_data[name] = {
        "name": name,
        "room": room,
        "status": status,
        "last_update": datetime.now().strftime("%H:%M:%S")
    }
    
    print(f">>> [多用户同步] 学生: {name} | 状态: {'在校' if status == 1 else '离校'}")
    return jsonify({"message": f"{name} 同步成功"}), 200

@app.route('/get_status', methods=['GET'])
def get_all_status():
    # 以前返回一个人的数据，现在直接返回整个“花名册”字典
    # 前端拿到后，可以用循环把所有人都画出来
    return jsonify(students_data)

if __name__ == '__main__':
    print("========================================")
    print("   多用户宿舍签到系统 - 后端已就绪        ")
    print("========================================")
    app.run(host='0.0.0.0', port=5000, debug=True)