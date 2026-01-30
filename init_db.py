import sqlite3

def setup_database():
    conn = sqlite3.connect('dormitory.db')
    c = conn.cursor()
    
    # 1. 创建表
    c.execute('''CREATE TABLE IF NOT EXISTS students 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                  name TEXT, 
                  uid TEXT UNIQUE, 
                  status INTEGER DEFAULT 0)''')

    # 2. 插入或更新数据 
    # 使用 INSERT OR REPLACE 确保如果 UID 变了也能更新
    target_uid = "5A E5 C6 CE 05 41 89"
    c.execute("INSERT OR REPLACE INTO students (id, name, uid) VALUES (1, 'Fangjia', ?)", (target_uid,))
    
    conn.commit()
    conn.close()
    print("Database synced: Thomas is now registered.")

if __name__ == "__main__":
    setup_database()