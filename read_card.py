import sqlite3
import time
import requests  # 新增：用于上网发信息的工具
from smartcard.System import readers
from smartcard.util import toHexString

# --- [产业化配置区] ---
# 这里是后端的地址。目前在本地跑，所以用 127.0.0.1
API_URL = "http://127.0.0.1:5000/update" 
# 必须和 app.py 里的暗号一模一样
API_KEY = "THOMAS_2026" 

def send_to_cloud(name, status):
    """
    这是一个新增的独立函数，专门负责‘发信’。
    它把名字和状态打包成 JSON 格式发给后端。
    """
    payload = {
        "name": name,
        "status": status  # 1 为在校，0 为离校
    }
    # 在信封头上贴上‘暗号’标签，确保后端认账
    headers = {"X-API-KEY": API_KEY}
    
    try:
        # 核心动作：向网址发起 POST 请求
        response = requests.post(API_URL, json=payload, headers=headers, timeout=3)
        if response.status_code == 200:
            print(f">>> [同步成功] 云端已更新为: {'在校' if status == 1 else '离校'}")
        else:
            print(f">>> [同步警告] 后端拒绝了数据，错误码: {response.status_code}")
    except Exception as e:
        # 如果你没开 app.py，或者断网了，这里会报错，但程序不会崩溃
        print(f">>> [同步跳过] 无法连接到后端，请检查 app.py 是否启动。")

def toggle_status(uid):
    """
    这是你的核心逻辑：刷卡 -> 改本地数据库 -> 发给云端
    """
    conn = sqlite3.connect('dormitory.db')
    c = conn.cursor()
    c.execute("SELECT name, status FROM students WHERE uid = ?", (uid,))
    result = c.fetchone()
    
    if result:
        name, current_status = result
        # 翻转状态：如果是 0 就变 1，如果是 1 就变 0
        new_status = 1 if current_status == 0 else 0
        
        # 1. 更新本地数据库（你的原始功能）
        c.execute("UPDATE students SET status = ? WHERE uid = ?", (new_status, uid))
        conn.commit()
        print(f"--- 本地记录 --- 学生: {name} | 动作: {'进入' if new_status == 1 else '离开'}")
        
        # 2. 同步到云端后端（新增功能）
        send_to_cloud(name, new_status)
        
    else:
        print(f"Unknown Card! UID: {uid}")
    
    conn.close()

# --- [主程序：读卡循环逻辑] ---
r = readers()
if len(r) == 0:
    print("没有找到读卡器，请检查连接！")
    exit()

reader = r[0]
print(f"正在使用读卡器: {reader}")
last_uid = None

while True:
    try:
        connection = reader.createConnection()
        connection.connect()
        # 获取卡片的 UID
        GET_UID = [0xFF, 0xCA, 0x00, 0x00, 0x00]
        data, sw1, sw2 = connection.transmit(GET_UID)
        uid = toHexString(data)
        
        if uid != last_uid:
            toggle_status(uid)
            last_uid = uid
            time.sleep(1) # 简单的防抖处理
    except:
        # 当卡片拿开时，重置记录，准备下一次刷卡
        last_uid = None
    time.sleep(0.5)