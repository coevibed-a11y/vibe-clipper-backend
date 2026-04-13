import cv2
import numpy as np
from collections import deque

class ImageDeduplicator:
    def __init__(self, threshold=0.85, memory_size=10):
        """
        :param threshold: 유사도 기준치 (0.0 ~ 1.0). 0.85면 85% 이상 똑같을 때 중복으로 판정
        :param memory_size: 최근 수확한 몇 장의 이미지를 기억할 것인가
        """
        self.threshold = threshold
        # deque(데크)를 사용해 최근 이미지들을 기억하는 '메모리 버퍼' 생성
        self.memory = deque(maxlen=memory_size)

    def is_duplicate(self, new_image):
        """새 이미지가 들어왔을 때 메모리의 이미지들과 비교하여 중복인지 판정"""
        if not self.memory:
            # 메모리가 비어있으면 무조건 첫 이미지이므로 통과 (기억해둠)
            self.memory.append(new_image)
            return False

        for saved_img in self.memory:
            similarity = self._calculate_similarity(new_image, saved_img)
            
            if similarity >= self.threshold:
                # 85% 이상 똑같이 생겼다면 중복으로 판정! (저장 안 함)
                return True

        # 메모리에 있는 어떤 이미지와도 겹치지 않는다면 새로운 데이터!
        self.memory.append(new_image)
        return False

    def _calculate_similarity(self, img1, img2):
        """두 이미지의 픽셀 단위 유사도를 계산하는 핵심 엔진 (가볍고 빠름)"""
        # 1. 비교를 위해 두 이미지의 크기를 64x64로 똑같이 맞춤
        img1_resized = cv2.resize(img1, (64, 64))
        img2_resized = cv2.resize(img2, (64, 64))

        # 2. 색상에 의한 오차를 줄이기 위해 흑백(Grayscale)으로 변환
        gray1 = cv2.cvtColor(img1_resized, cv2.COLOR_BGR2GRAY)
        gray2 = cv2.cvtColor(img2_resized, cv2.COLOR_BGR2GRAY)

        # 3. 두 이미지의 차이(Absolute Difference)를 계산
        diff = cv2.absdiff(gray1, gray2)
        
        # 4. 차이를 점수(0.0 ~ 1.0)로 환산 (1.0에 가까울수록 똑같은 이미지)
        similarity = 1.0 - (np.sum(diff) / (255.0 * 64 * 64))
        
        return similarity