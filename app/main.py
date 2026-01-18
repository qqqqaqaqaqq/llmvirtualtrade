# main.py
import time
import threading
from threading import Thread

from app.db.connection import get_connection
from app.db.base import Base
from app.db.session import engine, SessionLocal
from app.models.user import UserInformation
from app.services.worker import process

from app.core.globals import RUNNING_THREADS
from app.repositories.DBController import play_stop

# userid -> Thread 객체

def pull_db():
    play_stop("testuser")
    while True:
        db = SessionLocal()
        try:
            user_ids = [u.userid for u in db.query(UserInformation.userid).filter(UserInformation.play == True).all()]
            
            # 현재 실행중인 스레드 이름
            current_running = set(RUNNING_THREADS.keys())

            for userid in user_ids:
                if str(userid) not in current_running:
                    t = threading.Thread(
                        target=process,
                        name=str(userid),
                        args=(userid,),
                        daemon=True
                    )
                    t.start()
                    RUNNING_THREADS[str(userid)] = t

            # Play=False, tier=False면 스레드 제거 (종료는 daemon이므로 종료됨)
            for userid in list(RUNNING_THREADS.keys()):
                user = db.query(UserInformation).filter(UserInformation.userid == userid).first()
                if not user or not user.play:
                    RUNNING_THREADS.pop(userid, None)

        finally:
            db.close()

        time.sleep(5)  # 5초마다 체크

def startup():
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT NOW();")
        print("DB 연결 성공:", cur.fetchone())
        Base.metadata.create_all(bind=engine)
        conn.close()
    except Exception as e:
        print("DB 연결 실패:", e)

    t = Thread(
        target=pull_db, 
        daemon=True)
    t.start()

if __name__ == "__main__":
    startup()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("강제 종료")