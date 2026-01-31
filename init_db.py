# 修改后的 init_db.py
import sqlite3

def init():
    conn = sqlite3.connect('dormitory.db')
    c = conn.cursor()
    # 增加 room (房号) 字段
    # 增加 timestamp (最后活动时间) 字段，方便统计
    c.execute('''CREATE TABLE IF NOT EXISTS students
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  name TEXT,
                  uid TEXT UNIQUE,
                  room TEXT,
                  status INTEGER,
                  last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    conn.commit()
    conn.close()
    print(">>> 数据库地基已建好：支持姓名、UID、房号和自动时间戳。")

if __name__ == "__main__":
    init()