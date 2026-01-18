import os
import re
from datetime import datetime

BASE_LOG_DIR = "logs"
os.makedirs(BASE_LOG_DIR, exist_ok=True)


class UserLogger:
    def __init__(self, userid):
        self.userid = userid
        self.buffer = []

    def log(self, msg):
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.buffer.append(f"[{timestamp}] {msg}")

    def flush(self):
        if not self.buffer:
            return

        # --- userid 문자열 안전 변환 ---
        if isinstance(self.userid, str):
            user_id_str = self.userid
        else:
            try:
                user_id_str = str(self.userid.userid)
            except AttributeError:
                user_id_str = str(self.userid)

        user_id_str = re.sub(r'[^a-zA-Z0-9_-]', '_', user_id_str)

        # --- 날짜 폴더 ---
        today = datetime.now().strftime("%Y-%m-%d")
        user_dir = os.path.join(BASE_LOG_DIR, user_id_str)
        date_dir = os.path.join(user_dir, today)
        os.makedirs(date_dir, exist_ok=True)

        # --- 기존 로그 파일에서 최대 번호 찾기 ---
        max_num = 0
        for filename in os.listdir(date_dir):
            match = re.match(r"(\d{6})_", filename)
            if match:
                num = int(match.group(1))
                if num > max_num:
                    max_num = num

        # --- 다음 증가 번호 ---
        next_num = max_num + 1
        counter = f"{next_num:06d}"

        # --- 파일명 ---
        log_filename = f"{counter}_{user_id_str}.log"
        log_file = os.path.join(date_dir, log_filename)

        # --- 파일 저장 ---
        with open(log_file, "w", encoding="utf-8") as f:
            for entry in self.buffer:
                f.write(entry + "\n")

        self.buffer.clear()
        print(f"[{user_id_str}/{today}] 로그 저장 완료 → {log_filename}")
