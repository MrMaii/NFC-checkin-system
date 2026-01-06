import sqlite3

def setup_database():
    conn = sqlite3.connect('dormitory.db')
    c = conn.cursor()
    # 创建学生表
    c.execute('''CREATE TABLE IF NOT EXISTS students 
                 (uid TEXT PRIMARY KEY, name TEXT, room TEXT, grade TEXT)''')
    
    # 录入预设数据
    # 注意：'PENDING' 稍后需替换为真实 UID
    c.execute("INSERT OR REPLACE INTO students VALUES ('PENDING', 'Thomas', '218', 'Grade 11')")
    
    conn.commit()
    conn.close()
    print("Database 'dormitory.db' initialized successfully.")

if __name__ == "__main__":
    setup_database()