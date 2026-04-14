import subprocess
import re
import threading
import os
import time
from dotenv import load_dotenv
import firebase_admin
from firebase_admin import credentials, db

# 1. 환경 변수 및 Firebase 초기화
load_dotenv()
cred = credentials.Certificate("firebase-adminsdk.json")
firebase_admin.initialize_app(cred, {'databaseURL': os.getenv("FIREBASE_DB_URL")})

def run_cloudflared():
    print("☁️ [Manager] Cloudflare 터널을 백그라운드에서 실행합니다...")
    
    # 🌟 안전장치: 파일이 제대로 있는지 먼저 확인
    if not os.path.exists("cloudflared.exe"):
        print("❌ [Manager] 오류: 현재 폴더에 'cloudflared.exe' 파일이 없습니다! 파일 이름이나 위치를 확인해주세요.")
        return

    # 🌟 윈도우 환경에 맞춰 subprocess 실행 방식 완벽 개선 (shell=False, 인코딩 에러 무시)
    process = subprocess.Popen(
        ["cloudflared.exe", "tunnel", "--url", "http://localhost:8000"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding='utf-8',
        errors='ignore'
    )

    # 쏟아지는 로그를 한 줄씩 읽으며 감시
    for line in process.stdout:
        # 정규식(Regex)을 사용해 trycloudflare 주소만 정확히 낚아챔
        match = re.search(r"https://[a-zA-Z0-9-]+\.trycloudflare\.com", line)
        if match:
            cloud_url = match.group(0)
            print(f"\n🌍 [Manager] 터널 주소 획득 성공!: {cloud_url}")
            
            # 낚아챈 주소를 Firebase에 즉시 쏨
            try:
                ref = db.reference('server_status')
                ref.update({'backend_url': cloud_url, 'status': 'online'})
                print("🚀 [Manager] Firebase 자동 동기화 완료!\n")
            except Exception as e:
                print(f"❌ [Manager] Firebase 업데이트 실패: {e}")
            break # 목적을 달성했으니 감시 종료!

if __name__ == "__main__":
    # 1. 터널 실행 및 주소 훔치기 작업을 별도의 쓰레드(백그라운드)로 지시
    tunnel_thread = threading.Thread(target=run_cloudflared, daemon=True)
    tunnel_thread.start()

    # 2. 터널이 열릴 시간을 3초 정도로 넉넉히 줌 (Cloudflare 서버 응답 대기 시간 확보)
    time.sleep(3)
    
    # 3. 본체인 백엔드(FastAPI) 서버 가동!
    print("🔥 [Manager] 백엔드(FastAPI) 엔진을 가동합니다...")
    subprocess.run(["uvicorn", "app:app", "--reload"])