# src/engine.py
import cv2
from ultralytics import YOLO, SAM

class VibeClipperEngine:
    def __init__(self):
        # 1. 클래스가 생성될 때 모델을 딱 한 번만 메모리에 올립니다. (속도 최적화)
        print("⏳ Vibe 엔진 시동 중... (YOLO + SAM)")
        self.detector = YOLO("yolo11n.pt")
        self.segmenter = SAM("sam2_b.pt")
        print("✅ 엔진 시동 완료!")

    def crop_target(self, img_array, target_label="bird"):
        """
        텍스트(target)와 이미지(배열)를 받아서 크롭된 이미지 리스트를 반환합니다.
        """
        cropped_images = []
        
        # 1. 타겟 탐지
        detection_results = self.detector.predict(img_array, device="cuda", conf=0.55, verbose=False)
        
        target_boxes = []
        for det in detection_results[0].boxes:
            cls_id = int(det.cls[0])
            label = self.detector.names[cls_id]
            if label == target_label or label == "owl":
                target_boxes.append(det.xyxy[0].cpu().numpy())

        if not target_boxes:
            return cropped_images # 못 찾으면 빈 리스트 반환

        # 2. 정교한 크롭
        seg_results = self.segmenter.predict(img_array, bboxes=target_boxes, device="cuda", verbose=False)

        for result in seg_results:
            for box_data in result.boxes.xyxy:
                box = box_data.cpu().numpy().astype(int)
                x1, y1, x2, y2 = box
                cropped_images.append(img_array[y1:y2, x1:x2])

        return cropped_images