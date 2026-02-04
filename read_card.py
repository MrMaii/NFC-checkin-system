import requests
from smartcard.System import readers
from smartcard.util import toHexString

# ------------------ 树莓派 / 任意终端 读卡脚本 ------------------
# 把本地数据库的逻辑全部移到服务器端，由服务器根据 UID 查询并翻转状态。

# 后端服务器地址（部署好 Flask 的公网 IP 或域名）
# 示例：API_BASE = "http://123.123.123.123:5000"
API_BASE = "http://112.126.57.41:5000" # 部署到树莓派时改成你的服务器地址

API_SCAN_URL = f"{API_BASE}/scan"
API_KEY = "THOMAS_2026"


def send_scan(uid: str) -> None:
    """
    将刷到的 UID 发送到服务器，由服务器完成：
    - 根据 UID 查学生
    - 翻转 status
    - 更新 last_update
    """
    try:
        payload = {"uid": uid}
        headers = {"X-API-KEY": API_KEY}
        resp = requests.post(API_SCAN_URL, json=payload, headers=headers, timeout=5)

        if resp.status_code == 200:
            data = resp.json()
            name = data.get("name")
            status = data.get("status")
            time_str = data.get("time")
            action_text = "进入校内" if status == 1 else "离开校外"
            print(f">>> [刷卡成功] 学生: {name} | 动作: {action_text} | 时间: {time_str}")
        elif resp.status_code == 404:
            print(f"!!! [未知卡片] UID: {uid} 未在服务器数据库中登记，请先注册。")
        elif resp.status_code == 401:
            print("!!! [鉴权失败] 请检查 API_KEY 是否与服务器一致。")
        else:
            print(f"!!! [服务器错误] 状态码: {resp.status_code} | 响应: {resp.text}")
    except Exception as e:
        print(f"!!! [网络或系统错误] 无法上传刷卡数据: {e}")


def start_monitoring():
    """实时监控 NFC 读卡器（连接在树莓派或 PC 上）"""
    r = readers()
    if not r:
        print("未发现读卡器，请检查 USB 连接。")
        return

    reader = r[0]
    print("--- 宿舍管理系统硬件端已就绪 ---")
    print(f"正在监听读卡器: {reader}")
    print(f"目标服务器: {API_SCAN_URL}")

    last_uid = None
    while True:
        try:
            connection = reader.createConnection()
            connection.connect()

            # 获取 UID 的 APDU 指令
            GET_UID = [0xFF, 0xCA, 0x00, 0x00, 0x00]
            data, _, _ = connection.transmit(GET_UID)
            uid = toHexString(data)

            # 防止长按重复触发：只有当卡片离开再回来，或者换了一张卡才触发
            if uid != last_uid:
                send_scan(uid)
                last_uid = uid

        except Exception:
            # 这里的异常通常意味着卡片已移开 / 连接临时中断
            last_uid = None
            continue


if __name__ == "__main__":
    start_monitoring()