import sqlite3
import time
from smartcard.System import readers
from smartcard.util import toHexString

THOMAS_UID = "1D 69 BC A4 19 10 80" #

def toggle_status(uid):
    conn = sqlite3.connect('dormitory.db')
    c = conn.cursor()
    
    # Fetch current student info
    c.execute("SELECT name, status FROM students WHERE uid = ?", (uid,))
    result = c.fetchone()
    
    if result:
        name, current_status = result
        # Logic: If 0 (Out), set to 1 (In). If 1 (In), set to 0 (Out).
        new_status = 1 if current_status == 0 else 0
        action = "CHECKED-IN" if new_status == 1 else "CHECKED-OUT"
        
        # Update records
        c.execute("UPDATE students SET status = ? WHERE uid = ?", (new_status, uid))
        c.execute("INSERT INTO attendance_logs (student_name, action) VALUES (?, ?)", (name, action))
        
        conn.commit()
        print(f"\n[SYSTEM] {name} has {action}.")
        print(f"[STATUS] Location: {'Inside Dorm' if new_status == 1 else 'Outside'}")
    else:
        print(f"\n[ERROR] Unknown Card: {uid}")
    
    conn.close()

def run_scanner():
    r = readers()
    if not r:
        print("Reader not found.")
        return
    
    reader = r[0]
    print(f"Scanning via: {reader}")
    
    last_uid = None
    while True:
        try:
            connection = reader.createConnection()
            connection.connect()
            data, sw1, sw2 = connection.transmit([0xFF, 0xCA, 0x00, 0x00, 0x00])
            uid = toHexString(data)
            
            if uid != last_uid:
                toggle_status(uid)
                last_uid = uid
                time.sleep(1) # Prevent double-swiping
        except:
            last_uid = None
            time.sleep(0.1)

if __name__ == "__main__":
    run_scanner()