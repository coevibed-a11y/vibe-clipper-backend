import cv2
import os
from src.engine import VibeClipperEngine

def test_engine_initialization():
    """엔진이 에러 없이 잘 생성되는지 테스트합니다."""
    engine = VibeClipperEngine()
    assert engine.detector is not None
    assert engine.segmenter is not None

def test_crop_target_returns_list():
    """엔진에 이미지를 넣었을 때 리스트 형태의 결과물을 뱉어내는지 테스트합니다."""
    engine = VibeClipperEngine()
    
    # 테스트용 이미지 로드 (없으면 스킵하도록 처리)
    test_image_path = "data/owl_test.png"
    if not os.path.exists(test_image_path):
        assert False, f"테스트 이미지가 없습니다: {test_image_path}"
        
    img = cv2.imread(test_image_path)
    
    # 'bird' 타겟으로 크롭 실행
    results = engine.crop_target(img, target_label="bird")
    
    # 결과가 리스트 형태여야 하며, 최소 1개 이상의 이미지가 잘려야 함
    assert isinstance(results, list)
    assert len(results) > 0