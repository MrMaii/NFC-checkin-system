import sqlite3

def init():
    conn = sqlite3.connect('dormitory.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS students
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  name TEXT,
                  uid TEXT UNIQUE,
                  room TEXT,
                  email TEXT,
                  status INTEGER DEFAULT 0,
                  last_update TEXT DEFAULT '尚未刷卡')''') # 新增这一列
    conn.commit()
    conn.close()
    print(">>> 数据库已升级：支持存储后端生成的时间戳。")

if __name__ == "__main__":
    init()