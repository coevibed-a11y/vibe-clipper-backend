import os
import shutil
import time
import glob

class FileManager:
    def __init__(self, dataset_dir="dataset"):
        self.dataset_dir = dataset_dir
        # 폴더가 없으면 생성
        if not os.path.exists(self.dataset_dir):
            os.makedirs(self.dataset_dir)

    def clean_dataset_folder(self):
        """새로운 수확을 시작하기 전, 폴더 안의 이전 사진들을 싹 지워주는 기능"""
        print("🧹 [FileManager] 새로운 수확을 위해 기존 데이터를 청소합니다...")
        for filename in os.listdir(self.dataset_dir):
            file_path = os.path.join(self.dataset_dir, filename)
            try:
                if os.path.isfile(file_path):
                    os.remove(file_path)
            except Exception as e:
                print(f"파일 삭제 실패: {e}")

    def create_zip_and_cleanup(self) -> str:
        """현재 dataset 폴더를 압축하고, 예전 압축 파일은 지워서 용량을 아낌"""
        # 1. 새 압축 파일 이름 생성 (예: vibe_crops_1680000000.zip)
        timestamp = int(time.time())
        zip_base_name = f"{self.dataset_dir}/vibe_crops_{timestamp}"
        
        # 2. 압축 실행
        shutil.make_archive(zip_base_name, 'zip', self.dataset_dir)
        final_zip_name = f"{zip_base_name}.zip"
        print(f"📦 [FileManager] 압축 완료: {final_zip_name}")

        # 3. 용량 관리: 방금 만든 것 빼고, 옛날 zip 파일들은 다 지워버림
        all_zips = glob.glob(f"{self.dataset_dir}/*.zip")
        for old_zip in all_zips:
            # 백슬래시/슬래시 차이 무시하고 파일명 비교
            if os.path.normpath(old_zip) != os.path.normpath(final_zip_name):
                os.remove(old_zip)
                print(f"🗑️ [FileManager] 용량 확보를 위해 이전 파일 삭제: {old_zip}")

        # 프론트엔드에 전달할 파일 이름만 리턴
        return f"vibe_crops_{timestamp}.zip"