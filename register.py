# 新建文件: register.py
import sqlite3
from smartcard.System import readers
from smartcard.util import toHexString

def interactive_register():
    conn = sqlite3.connect('dormitory.db')
    c = conn.cursor()
    
    # 确保表里有 room 字段 (如果之前没有，这里会增加)
    try:
        c.execute("ALTER TABLE students ADD COLUMN room TEXT")
    except:
        pass # 如果已经有了就跳过

    print(">>> 交互式学生注册系统已启动")
    print(">>> 请将新的 NFC 卡片放置在读卡器上...")

    r = readers()
    if len(r) == 0: return print("未找到读卡器")
    reader = r[0]

    while True:
        try:
            connection = reader.createConnection()
            connection.connect()
            GET_UID = [0xFF, 0xCA, 0x00, 0x00, 0x00]
            data, _, _ = connection.transmit(GET_UID)
            uid = toHexString(data)
            
            # 检查是否已存在
            c.execute("SELECT name FROM students WHERE uid = ?", (uid,))
            existing = c.fetchone()
            if existing:
                print(f"警告：该卡片已被 {existing[0]} 注册。")
                continue

            print(f"\n[检测到新卡片] UID: {uid}")
            name = input("请输入学生姓名: ")
            room = input("请输入房间号: ")

            # 写入数据库
            c.execute("INSERT INTO students (name, uid, room, status) VALUES (?, ?, ?, 0)", 
                      (name, uid, room))
            conn.commit()
            print(f"成功！学生 {name} (房间 {room}) 已存入数据库。")
            print("\n等待下一张卡片...")
            
        except Exception as e:
            pass # 循环等待刷卡

if __name__ == "__main__":
    interactive_register()