# sqlalchemy
from sqlalchemy.exc import SQLAlchemyError

# system
from datetime import timezone, timedelta
import time
import traceback

# db
from app.db.session import SessionLocal

# models
from app.models.trading import TradingHistory
from app.models.user import UserInformation

# db controller
from app.repositories.DBController import play_stop

# global
from app.core.globals import *

# services
from app.services.call_api.apitest import test_api
from app.services.flow_process import flow_main

# logger
from app.utils.logger import UserLogger

def get_user_and_history(userid: str):
    db = SessionLocal()
    try:
        user = db.query(UserInformation).filter(UserInformation.userid == userid).first()
        trade_history = (
            db.query(TradingHistory)
            .filter(TradingHistory.userid == userid)
            .order_by(TradingHistory.createdtime.desc())
            .limit(5)
            .all()
        )
        return user, trade_history
    except SQLAlchemyError as e:
        print("DB 오류:", e)
        return None, None
    finally:
        db.close()

# main process
def process(userid:str):
    # user 기록 시작
    user_logger = UserLogger(userid)
    
    if userid != "testuser":
        return
    
    user, trade_history = get_user_and_history(userid=userid)
    start_time_utc = user.start_time.astimezone(timezone.utc)
    end_time_utc = user.end_time.astimezone(timezone.utc)

    trade_interval = user.trade_interval
    current_time = start_time_utc
    

    # 쓰레드가 자동 종료 되지 않도록 무한 반복
    while current_time < end_time_utc:

        print(f"test 시작 시간 : {current_time}")
        # 진행 전엔 항상 stable false        
        stable = False
        # 재시도
        for i in range(ATTEMP):
            try:
                # wait때 변경될 수도 있으므로 재 검색
                user, trade_history = get_user_and_history(userid=userid)

                # db 검색시 문제가 발생할 경우 정상 종료 하고 재 시도
                if not user:
                    raise ValueError(f"{userid} information search error")
                
                # 현재 시간 = utc
                user_logger.log(f"ID : {userid}")
                user_logger.log(f"작성 시간 : {current_time}")    

                # 검증
                if not user.play: user_logger.log("play False"); break

                if not user.llm_model: user_logger.log(f"{userid} : Model 미 지정"); continue
            
                # api 모델 테스트
                api_key = None
                model = user.llm_model

                if "GPT" in model:
                    api_key = user.openai
                elif "GEMINI" in model:
                    api_key = user.gemma
                elif "GROK" in model:
                    api_key = user.grok
                else:
                    api_key = None

                if api_key == None:
                    user_logger.log(f"{userid} : API 키 확인 불가")
                    break    

                if not test_api(usemodel=user.llm_model, api_key=api_key, user_logger=user_logger):
                    user_logger.log(f"{userid} : LLM 키 검증 실패")
                    raise ValueError(f"{userid} information search error")
            
                usertic:dict = user.ticker
                ticker = []
                for key, val in usertic.items():
                    if val:
                        ticker.append(key)

                if not ticker:
                    user_logger.log(f"{userid} : 티커 미 지정")
                    break

                user_logger.log(f"{ticker}")

                trading_fee = user.trading_fee
                user_prompt = user.userprompt    
                trade_interval = user.trade_interval
                
                print(f"userid : {userid} start")
                flow_process = flow_main(
                    user=user,
                    userid=userid,
                    current_time=current_time,
                    exchange=user.exchange,
                    trade_fee=trading_fee,
                    api_key=api_key,
                    ticker=ticker,
                    user_prompt=user_prompt,
                    _trade_history=trade_history,
                    usemodel = user.llm_model,
                    trade_interval=trade_interval,
                    user_logger = user_logger
                )

                # flow_process 실패시 내부 횟수도 모두 소진 상태
                # 최소 각 파트 15번씩이라 실패면 아예 문제 있는걸로 판단해야됨
                if flow_process == False:
                    print(f"userid : {userid} 작성 실패 log 기록 확인 바랍니다")
                    stable = False
                    break

                # 모든 조건이 완료 되었을때 for 문 탈출
                stable = True
                user_logger.log(f"userid : {userid} 정상 완료")
                break
            
            # error 발생시 재 시도
            except Exception as e:
                tb = traceback.format_exc()
                user_logger.log(f"Error:\n{tb}")
                user_logger.log(f"{e}")
            finally:
                time.sleep(1)

        # 완료되면 user_logger 배포
        user_logger.flush()

        # for 문이 끝났는데도 stable이 false 인 경우 모든 횟수 차감
        if stable == False:
            break
        else:
            current_time += timedelta(seconds=trade_interval)

    # while 탈출 시 안전하게 play : stop 처리
    play_stop(userid=userid)
    user_logger.flush()
    
