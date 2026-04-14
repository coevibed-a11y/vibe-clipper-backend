import requests
import firebase_admin
import os
import cv2

# 로컬 모듈 임포트
from firebase_admin import credentials, db
from fastapi import FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

# 로컬 엔진과 유틸리티 모듈 임포트
from src.engine import VibeClipperEngine
from src.youtube import YouTubeStreamer
from src.video import VideoProcessor
from dotenv import load_dotenv

# 스마트 필터 및 파일 관리 모듈 임포트
from src.deduplicator import ImageDeduplicator
from src.time_manager import TimeManager
from src.file_manager import FileManager

# ==========================================
# 1. 환경 변수(.env) 로드 및 보안 설정 적용
# ==========================================
load_dotenv() # .env 파일 읽어오기

# .env 파일에서 비밀 장부 값 꺼내오기
DATABASE_URL = os.getenv("FIREBASE_DB_URL")
API_KEY_SECRET = os.getenv("VIBE_API_KEY")

# ==========================================
# 2. Firebase 초기화
# ==========================================
cred = credentials.Certificate("firebase-adminsdk.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': DATABASE_URL # 이제 깃허브에 주소가 노출되지 않습니다!
})

app = FastAPI(title="Vibe-Clipper API")

# ==========================================
# 3. FastAPI 미들웨어 및 정적 파일 설정
# ==========================================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if not os.path.exists("dataset"):
    os.makedirs("dataset")
app.mount("/dataset", StaticFiles(directory="dataset"), name="dataset")

# ==========================================
# 4. AI 엔진 및 스트리머 전역 로드
# ==========================================
engine = VibeClipperEngine()
yt_streamer = YouTubeStreamer()

# 스마트 필터 가동 (70% 이상 똑같으면 버림, 최근 10장 기억)
deduplicator = ImageDeduplicator(threshold=0.7, memory_size=10)

class CropRequest(BaseModel):
    youtube_url: str
    target_label: str = "bird"
    max_crops: int = 5
    start_time: str = "00:00:00"  # (기본값 0초)
    end_time: str = "00:05:00"    # (기본값 5분)

# ==========================================
# 6. 메인 API 엔드포인트
# ==========================================
@app.post("/api/mine")
async def mine_video(
    request: CropRequest, 
    x_api_key: str = Header(None)  
):
    # 보안 로직 (환경 변수에서 가져온 API_KEY_SECRET과 비교)
    if x_api_key != API_KEY_SECRET:
        raise HTTPException(status_code=401, detail="API Key가 틀렸거나 없습니다! 접근 금지 🚫")

    print(f"🌐 웹에서 요청이 들어왔습니다! 타겟: {request.target_label}")
    
    stream_url = yt_streamer.get_direct_url(request.youtube_url)
    if not stream_url:
        return {"status": "error", "message": "유튜브 스트림을 가져올 수 없습니다."}

    # 🌟 [추가] 이번 요청을 위한 매니저들 등판
    time_mgr = TimeManager(request.start_time, request.end_time)
    file_mgr = FileManager("dataset")
    
    # 🌟 [추가] 수확 시작 전 폴더 싹 비우기! (이전 데이터 섞임 방지)
    file_mgr.clean_dataset_folder()
    
    video_proc = VideoProcessor(target_fps=1)
    total_crops = 0
    saved_files = []

    print(f"🎬 {request.start_time} 부터 수확을 시작합니다...")

    # 파이프라인 가동!
    # time_sec는 현재 프레임의 시간(초)을 의미합니다.
    for time_sec, frame in video_proc.extract_frames_stream(stream_url):
        
        # 🌟 1. 아직 시작 시간이 안 됐다면? -> 쿨하게 패스 (빨리 감기)
        if not time_mgr.is_time_to_start(time_sec):
            continue 
            
        # 🌟 2. 종료 시간이 지났다면? -> 칼퇴근! (파이프라인 즉시 종료)
        if time_mgr.is_time_to_stop(time_sec):
            print("🛑 [수확 종료] 설정한 종료 시간에 도달했습니다.")
            break 
            
        # --- (이 아래는 기존에 작성하신 수확 & 필터링 로직 그대로 유지) ---
        cropped_images = engine.crop_target(frame, target_label=request.target_label)
        
        for crop_img in cropped_images:
            #if deduplicator.is_duplicate(crop_img):
            #    continue

            filename = f"dataset/gold_{request.target_label}_{total_crops}.png"
            cv2.imwrite(filename, crop_img)
            saved_files.append(filename)
            total_crops += 1
            
            if total_crops >= request.max_crops:
                # 🌟 [수정] 모듈을 통해 압축하고, URL 받기
                zip_filename = file_mgr.create_zip_and_cleanup()
                
                return {
                    "status": "success", 
                    "message": f"최대 수확량(50장) 도달! 고순도 에셋 압축 완료",
                    "files": saved_files,
                    "zip_url": f"dataset/{zip_filename}" # 다운로드 링크
                }

    # 영상이 다 끝났을 때
    if total_crops > 0:
        zip_filename = file_mgr.create_zip_and_cleanup()
        zip_url = f"dataset/{zip_filename}"
    else:
        zip_url = None

    return {
        "status": "success", 
        "message": f"작업 완료 (총 {total_crops}장 수확)", 
        "files": saved_files,
        "zip_url": zip_url
    }