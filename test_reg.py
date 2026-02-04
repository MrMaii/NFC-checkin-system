import sqlite3
from smartcard.System import readers
from smartcard.util import toHexString
import time

# --- 配置 ---
DB_PATH = 'dormitory.db'
# 中文数字映射，方便生成“测试一”到“测试十一”
CHINESE_NUMS = ["", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11"]

def get_card_uid(reader):
    """阻塞式等待刷卡并获取 UID"""
    print(">>> 请刷卡...")
    while True:
        try:
            connection = reader.createConnection()
            connection.connect()
            # 获取 UID 的指令
            GET_UID = [0xFF, 0xCA, 0x00, 0x00, 0x00]
            data, _, _ = connection.transmit(GET_UID)
            return toHexString(data)
        except Exception:
            # 如果没刷卡，稍微等一下继续试
            time.sleep(0.5)
            continue

def batch_register():
    # 1. 检查读卡器
    r = readers()
    if not r:
        print("未发现读卡器，请检查 USB 连接。")
        return
    reader = r[0]

    # 2. 连接数据库
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    print(f"=== 开始批量录入测试账号 (共 11 个) ===")

    for i in range(1, 12):
        # 生成测试数据
        name = f"Test_{CHINESE_NUMS[i]}"
        room = f"{i:03d}"  # 格式化为 001, 002...
        email = f"@{i}"
        
        print(f"\n------------------------------------")
        print(f"当前准备录入：")
        print(f"姓名：{name}")
        print(f"房号：{room}")
        print(f"邮箱：{email}")
        
        # 3. 等待刷卡获取 UID
        uid = get_card_uid(reader)
        print(f"成功识别 UID: {uid}")

        try:
            # 4. 写入数据库
            c.execute('''INSERT INTO students (name, uid, room, email, status, last_update) 
                         VALUES (?, ?, ?, ?, ?, ?)''', 
                      (name, uid, room, email, 0, "未刷卡"))
            conn.commit()
            print(f"✅ {name} 录入成功！")
        except sqlite3.IntegrityError:
            print(f"❌ 录入失败：UID {uid} 或姓名已存在（跳过此人）。")
        
        # 提示用户拿开卡片，准备下一次
        print("请移开卡片，准备下一个...")
        time.sleep(2)

    conn.close()
    print("\n=== 所有 11 个测试账号处理完毕 ===")

if __name__ == "__main__":
    batch_register()