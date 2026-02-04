import requests
from smartcard.System import readers
from smartcard.util import toHexString

# ------------------ 树莓派 / 任意终端 注册脚本 ------------------
# 读卡 + 人工输入信息，然后把数据发到服务器，由服务器写入 dormitory.db

# 示例：API_BASE = "http://123.123.123.123:5000"
API_BASE = "http://112.126.57.41:5000" # 部署到树莓派时改成你的服务器地址

API_REGISTER_URL = f"{API_BASE}/register_student"
API_KEY = "THOMAS_2026"


def interactive_register():
    print(">>> 请刷入新同学的 NFC 卡片（读卡器需连接在本机/树莓派上）...")

    r = readers()
    if not r:
        print("未发现读卡器，请检查 USB 连接。")
        return

    reader = r[0]

    while True:
        try:
            connection = reader.createConnection()
            connection.connect()
            GET_UID = [0xFF, 0xCA, 0x00, 0x00, 0x00]
            data, _, _ = connection.transmit(GET_UID)
            uid = toHexString(data)

            print(f"\n[卡片识别成功] UID: {uid}")
            name = input("请输入学生姓名: ").strip()
            room = input("请输入房间号 (如 302): ").strip()
            email = input("请输入邮箱账号: ").strip()

            if not all([name, room, email]):
                print("!!! 有必填项为空，请重新刷卡并输入。")
                continue

            payload = {
                "name": name,
                "uid": uid,
                "room": room,
                "email": email,
            }
            headers = {"X-API-KEY": API_KEY}

            try:
                resp = requests.post(
                    API_REGISTER_URL, json=payload, headers=headers, timeout=5
                )
            except Exception as e:
                print(f"!!! [网络错误] 无法连接服务器: {e}")
                continue

            if resp.status_code == 201:
                print(f"成功注册：{name} | 房间：{room} | 邮箱：{email}")
                break
            elif resp.status_code == 409:
                print("!!! 该 UID 已存在，请勿重复注册（可以直接刷卡测试出入）。")
                break
            elif resp.status_code == 401:
                print("!!! 鉴权失败，请检查 API_KEY 是否与服务器一致。")
                break
            else:
                print(f"!!! 服务器返回错误: {resp.status_code} | {resp.text}")
                break

        except Exception:
            # 多半是读卡过程中的错误/卡片移开，继续等待下一次
            continue


if __name__ == "__main__":
    interactive_register()