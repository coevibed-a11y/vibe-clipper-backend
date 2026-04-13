# src/youtube.py
import yt_dlp

class YouTubeStreamer:
    def __init__(self):
        # 1080p 이하의 mp4 포맷을 스트리밍하기 좋은 형태로 옵션 설정
        self.ydl_opts = {
            'format': 'best[ext=mp4]/best',
            'quiet': True,
            'noplaylist': True
        }

    def get_direct_url(self, youtube_url):
        """유튜브 URL을 받아 다운로드 없이 순수 스트림 주소만 반환합니다."""
        print(f"📡 유튜브 스트림 연결 중... ({youtube_url})")
        try:
            with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
                info = ydl.extract_info(youtube_url, download=False)
                return info['url']
        except Exception as e:
            print(f"❌ 유튜브 스트림 추출 실패: {e}")
            return None