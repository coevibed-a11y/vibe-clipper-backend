from fastapi import FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware # CORS 추가
from fastapi.staticfiles import StaticFiles # 정적 파일 제공 추가
from pydantic import BaseModel
import os
import cv2
from src.engine import VibeClipperEngine
from src.youtube import YouTubeStreamer
from src.video import VideoProcessor

app = FastAPI(title="Vibe-Clipper API")

# 0. CORS 설정 (Next.js 웹 화면에서 API를 호출할 수 있게 허용)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # 포폴용이므로 일단 모두 허용
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 1. 이미지 폴더 개방 (Next.js가 dataset 폴더의 이미지를 가져갈 수 있게 함)
if not os.path.exists("dataset"):
    os.makedirs("dataset")
app.mount("/dataset", StaticFiles(directory="dataset"), name="dataset")

API_KEY_SECRET = "my_vibe_secret_123"

# 2. 엔진들은 서버가 켜질 때 딱 한 번만 로드되도록 전역 변수로 세팅
engine = VibeClipperEngine()
yt_streamer = YouTubeStreamer()

# 3. 프론트엔드(웹)에서 받을 데이터 형식 정의
class CropRequest(BaseModel):
    youtube_url: str
    target_label: str = "bird"
    max_crops: int = 5

# 4. API 엔드포인트 생성 (이 주소로 요청이 들어오면 작업 시작!)
@app.post("/api/mine")
async def mine_video(request: CropRequest):
    print(f"🌐 웹에서 요청이 들어왔습니다! 타겟: {request.target_label}")
    
    stream_url = yt_streamer.get_direct_url(request.youtube_url)
    if not stream_url:
        return {"status": "error", "message": "유튜브 스트림을 가져올 수 없습니다."}

    if not os.path.exists("dataset"):
        os.makedirs("dataset")

    video_proc = VideoProcessor(target_fps=1)
    total_crops = 0
    saved_files = []

    # 파이프라인 가동!
    for time_sec, frame in video_proc.extract_frames_stream(stream_url):
        cropped_images = engine.crop_target(frame, target_label=request.target_label)
        
        for crop_img in cropped_images:
            filename = f"dataset/gold_{request.target_label}_{total_crops}.png"
            cv2.imwrite(filename, crop_img)
            saved_files.append(filename)
            total_crops += 1
            
            if total_crops >= request.max_crops:
                return {
                    "status": "success", 
                    "message": f"총 {total_crops}장의 데이터 수확 완료!",
                    "files": saved_files
                }

    return {"status": "success", "message": "작업이 완료되었습니다.", "files": saved_files}
