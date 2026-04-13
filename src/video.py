# src/video.py
import cv2

class VideoProcessor:
    def __init__(self, target_fps=1):
        # target_fps: 1초당 몇 장의 사진을 뽑을 것인가? (기본 1장)
        self.target_fps = target_fps

    def extract_frames_stream(self, stream_url):
        """스트림 주소를 열어 실시간으로 프레임을 하나씩 뱉어냅니다(yield)."""
        cap = cv2.VideoCapture(stream_url)
        
        if not cap.isOpened():
            print("❌ 스트림을 열 수 없습니다.")
            return

        # 원본 영상의 FPS 확인 (보통 30 또는 60)
        video_fps = int(cap.get(cv2.CAP_PROP_FPS))
        # 몇 프레임마다 한 장씩 뽑을지 계산 (예: 60fps 영상에서 1fps를 원하면 60프레임마다 1장)
        frame_skip = max(1, video_fps // self.target_fps)

        frame_count = 0
        extracted_count = 0

        print(f"🎞️ 프레임 추출 시작 (1초당 {self.target_fps}장)")

        while True:
            ret, frame = cap.read()
            if not ret:
                break # 영상 끝

            # 지정된 간격(1초)마다 프레임을 밖으로 던짐(yield)
            if frame_count % frame_skip == 0:
                extracted_count += 1
                yield extracted_count, frame

            frame_count += 1

        cap.release()
        print("🎬 영상 스트림 종료.")