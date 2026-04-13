class TimeManager:
    def __init__(self, start_time_str="00:00:00", end_time_str="00:05:00"):
        """
        :param start_time_str: "MM:SS" 또는 "HH:MM:SS" 형태의 시작 시간
        :param end_time_str: "MM:SS" 또는 "HH:MM:SS" 형태의 종료 시간
        """
        self.start_sec = self._parse_to_seconds(start_time_str)
        self.end_sec = self._parse_to_seconds(end_time_str)
        print(f"🕒 [TimeManager] 수확 구간 설정 완료: {self.start_sec}초 ~ {self.end_sec}초")

    def _parse_to_seconds(self, time_str: str) -> int:
        """'01:20' 같은 문자열을 80초(int)로 변환하는 핵심 로직"""
        if not time_str:
            return 0
            
        parts = time_str.split(':')
        parts.reverse()  # 초, 분, 시 순서로 뒤집기
        
        seconds = 0
        for i, part in enumerate(parts):
            seconds += int(part) * (60 ** i)
        return seconds

    def is_time_to_start(self, current_sec: float) -> bool:
        """현재 영상 재생 시간이 시작 시간을 넘었는지 확인"""
        return current_sec >= self.start_sec

    def is_time_to_stop(self, current_sec: float) -> bool:
        """현재 영상 재생 시간이 종료 시간을 넘었는지 확인"""
        return current_sec > self.end_sec