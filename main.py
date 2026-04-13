# main.py
import cv2
import os
from src.engine import VibeClipperEngine
from src.youtube import YouTubeStreamer
from src.video import VideoProcessor

def run_vibe_clipper(youtube_url, target_label="bird", max_crops=10):
    # 1. 모듈 준비
    engine = VibeClipperEngine()
    yt_streamer = YouTubeStreamer()
    video_proc = VideoProcessor(target_fps=1) # 1초에 1장 검사

    # 2. 파이프라인 가동: 유튜브 URL -> 스트림 주소
    stream_url = yt_streamer.get_direct_url(youtube_url)
    if not stream_url:
        return

    if not os.path.exists("dataset"):
        os.makedirs("dataset")

    total_crops = 0

    # 3. 파이프라인 가동: 스트림 주소 -> 1초마다 프레임 추출 -> 엔진 크롭
    for time_sec, frame in video_proc.extract_frames_stream(stream_url):
        print(f"👀 {time_sec}초 부근 프레임 분석 중...")
        
        # 엔진에 이미지 던져서 부엉이 수확
        cropped_images = engine.crop_target(frame, target_label=target_label)
        
        for crop_img in cropped_images:
            # 수확된 이미지를 파일로 저장
            filename = f"dataset/gold_{target_label}_{total_crops}.png"
            cv2.imwrite(filename, crop_img)
            total_crops += 1
            print(f"🎯 [{total_crops}] {target_label} 크롭 성공! -> {filename}")
            
            # 테스트를 위해 너무 많이 돌지 않게 제한 (10장 찾으면 종료)
            if total_crops >= max_crops:
                print(f"🛑 목표 수량({max_crops}장) 달성. 공장을 멈춥니다.")
                return

if __name__ == "__main__":
    # 테스트용 부엉이 영상 URL (짧은 쇼츠나 다큐멘터리 링크를 넣으세요!)
    test_url = "https://www.youtube.com/shorts/0B-MjnE55zc"  # <--- 여기에 유튜브 링크 입력!
    run_vibe_clipper(test_url, target_label="bird", max_crops=5)