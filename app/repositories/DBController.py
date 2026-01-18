# sqlalchemy
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import text

# 시스템
from datetime import datetime, timezone

# 앱 내부
from app.db.session import SessionLocal
from app.models.user import UserInformation
from app.models.trading import TradingHistory
from app.core.settings import settings

# 암호화
from cryptography.fernet import Fernet

def trade_insert(userid:str, data:dict):
    db = SessionLocal()
    try:
        trade:TradingHistory=TradingHistory(
            userid=userid,
            createdtime = data.get("createdtime", datetime.min),
            position=data.get("position", {}),
            why=data.get("why", {}),
            exchange=data.get("exchange", ""),
            trade_history=data.get("trade_history", {}),
            available_cash = data.get("available_cash", 0),
            avg_list = data.get("avg_list", {}),
            owner_coin = data.get("owner_coin", {}),
            total = data.get("total", 0.0)
        )

        db.add(trade)
        db.commit()
        print("db save")   
    except SQLAlchemyError as e:
        db.rollback()
        print("DB 오류:", e)
    except Exception as e:
        db.rollback()
        print("알 수 없는 오류:", e)
    finally:
        db.close()

def init_trade_insert():
    db = SessionLocal()
    try:
        trade:TradingHistory=TradingHistory(
            id=1,
            userid="testuser",
            createdtime = datetime.now(timezone.utc),
            position={},
            why={},
            exchange="Upbit",
            trade_history={},
            available_cash = 100_000_000,
            avg_list = {},
            owner_coin = {},
            total = 100_000_000
        )
        db.add(trade)
        db.commit()            
    except SQLAlchemyError as e:
        db.rollback()
        print("DB 오류:", e)
    except Exception as e:
        db.rollback()
        print("알 수 없는 오류:", e)
    finally:
        db.close()

def user_insert(
    ticker, userprompt, llm_model,
    openai, grok, gemma, userid,
    trade_interval, trading_fee,
    start_time, end_time
):
    db = SessionLocal()
    try:
        user = db.query(UserInformation)\
                 .filter(UserInformation.userid == userid)\
                 .first()

        if user:
            # ===== UPDATE =====
            user.ticker = ticker
            user.userprompt = userprompt
            user.llm_model = llm_model
            user.openai = openai
            user.grok = grok
            user.gemma = gemma
            user.trade_interval = trade_interval
            user.trading_fee = trading_fee
            user.start_time = start_time
            user.end_time = end_time            
        else:
            # ===== INSERT =====
            user = UserInformation(
                userid="testuser",
                play=False,
                ticker=ticker,
                userprompt=userprompt,
                llm_model=llm_model,
                openai=openai,
                grok=grok,
                gemma=gemma,
                trade_interval=trade_interval,
                trading_fee=trading_fee,
                start_time=start_time,
                end_time=end_time
            )
            db.add(user)

        db.commit()

    except SQLAlchemyError as e:
        db.rollback()
        print("DB 오류:", e)
    except Exception as e:
        db.rollback()
        print("알 수 없는 오류:", e)
    finally:
        db.close()
# 정보 변경
def play_stop(userid:str):
    db = SessionLocal()    
    try:
        user:UserInformation = db.query(UserInformation).filter_by(userid=userid).first()
        if not user:
            return {"status": "fail", "error": "User not found"}
        user.play = False
        db.commit()
        return {"status": "success"}
    except SQLAlchemyError as e:
        db.rollback()
        print("DB 오류:", e)
    except Exception as e:
        db.rollback()
        print("알 수 없는 오류:", e)
    finally:
        db.close()


def delete_trade_insert():
    db = SessionLocal()
    try:
        # id = 1 제외하고 전부 삭제
        db.query(TradingHistory)\
          .filter(TradingHistory.id != 1)\
          .delete(synchronize_session=False)

        # PostgreSQL: 시퀀스 리셋
        # trading_history_id_seq 이름은 실제 시퀀스 이름으로 변경 필요
        db.execute(text("ALTER SEQUENCE trading_history_id_seq RESTART WITH 2"))

        db.commit()

    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()