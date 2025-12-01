import time
import re
import requests
import os
from dotenv import load_dotenv

# 1. 설정
# 라즈베리 파이의 IP 주소 (예: 192.168.0.10)를 입력하세요.
# 라즈베리 파이에서 'hostname -I' 명령어로 IP 확인 가능
RASPBERRY_PI_IP = "127.0.0.1" 
API_URL = f"http://{RASPBERRY_PI_IP}:8000/log"

# PC에 있는 마인크래프트 로그 파일 경로 (본인 환경에 맞게 수정!)
LOG_FILE_PATH = os.getenv("MINECRAFT_LOG_PATH", "logs/latest.log")

if not os.path.exists(LOG_FILE_PATH):
    print(f"⚠️ 경고: 로그 파일을 찾을 수 없습니다: {LOG_FILE_PATH}")
    print("💡 .env 파일에 MINECRAFT_LOG_PATH를 설정하거나 경로를 확인하세요.")


def tail_log_file(path):
    print(f"📂 Watching log file: {path}")
    while not os.path.exists(path):
        print(f"Waiting for log file at {path}...")
        time.sleep(5)
    
    with open(path, "r", encoding="utf-8", errors='ignore') as f:
        f.seek(0, 2)
        while True:
            line = f.readline()
            if not line:
                time.sleep(0.1)
                continue
            yield line

def main():
    active_sessions = {}
    join_pattern = re.compile(r": (\w+) joined the game")
    left_pattern = re.compile(r": (\w+) left the game")

    print(f"📤 Log Sender Started")
    print(f"🎯 Target API: {API_URL}")

    try:
        for line in tail_log_file(LOG_FILE_PATH):
            if join_match := join_pattern.search(line):
                username = join_match.group(1)
                active_sessions[username] = time.time()
                print(f"🟢 User Joined: {username}")
                
            if left_match := left_pattern.search(line):
                username = left_match.group(1)
                if username in active_sessions:
                    start_time = active_sessions.pop(username)
                    duration = int(time.time() - start_time)
                    print(f"🔴 User Left: {username} ({duration}s) -> Sending...", end=" ")
                    
                    try:
                        res = requests.post(API_URL, json={"username": username, "duration": duration}, timeout=5)
                        if res.status_code == 200:
                            print("✅ Sent Success")
                        else:
                            print(f"❌ Failed: {res.text}")
                    except Exception as e:
                        print(f"❌ Network Error: Is Raspberry Pi on? ({e})")
    except KeyboardInterrupt:
        print("\n🛑 Log Sender Stopped")

if __name__ == "__main__":
    main()

