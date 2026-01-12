from smartcard.System import readers
from smartcard.util import toHexString
import time

def get_uid():
    r = readers()
    if not r:
        print("Error: No reader detected. Check USB connection.")
        return None
    
    reader = r[0]
    print(f"Using reader: {reader}")
    print("Waiting for card tap...")
    
    while True:
        try:
            connection = reader.createConnection()
            connection.connect()
            # Standard PCSC command to get card UID
            GET_DATA = [0xFF, 0xCA, 0x00, 0x00, 0x00]
            data, sw1, sw2 = connection.transmit(GET_DATA)
            
            if sw1 == 0x90:
                uid = toHexString(data)
                print(f"Captured UID: {uid}")
                return uid
        except Exception:
            pass
        time.sleep(0.5)

if __name__ == "__main__":
    get_uid()