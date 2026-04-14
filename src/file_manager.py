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
        timestamp = int(time.time())
        final_zip_name = f"vibe_crops_{timestamp}.zip"
        final_zip_path = os.path.join(self.dataset_dir, final_zip_name)

        # 🚨 [핵심 수정] 무한 압축 버그(Zip Bomb) 차단!
        # 1. 압축 파일을 dataset 폴더 바깥(현재 작업 폴더의 최상위)에 임시로 만듭니다.
        temp_zip_base = f"temp_vibe_crops_{timestamp}"
        shutil.make_archive(temp_zip_base, 'zip', self.dataset_dir)
        
        # 2. 다 만들어진 임시 압축 파일을 dataset 폴더 안으로 안전하게 이동시킵니다.
        shutil.move(f"{temp_zip_base}.zip", final_zip_path)
        
        print(f"📦 [FileManager] 압축 완료: {final_zip_name}")

        # 3. 용량 관리: 방금 만든 것 빼고, 옛날 zip 파일들은 다 지워버림
        all_zips = glob.glob(f"{self.dataset_dir}/*.zip")
        for old_zip in all_zips:
            if os.path.normpath(old_zip) != os.path.normpath(final_zip_path):
                os.remove(old_zip)
                print(f"🗑️ [FileManager] 용량 확보를 위해 이전 파일 삭제: {old_zip}")

        return final_zip_name