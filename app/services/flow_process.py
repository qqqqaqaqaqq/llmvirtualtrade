# system
import json
import  time
import traceback
import datetime
import pandas as pd
from dateutil.parser import isoparse

# global
from app.core.globals import *

# 앱 내부
from app.services.indicators import indicater_generate

# Prompt
from app.services.prompt import PromptGeneration

# Model
from app.services.call_api.gemini import gemini_2_5_pro, gemini_3_flash_preview
from app.services.call_api.gpt import gpt_5_mini
from app.services.call_api.grok import grok_3_mini

# Exchange
from app.services.exchanges.exchange_mapping import EXCHANGE_MAP
from app.services.exchanges.base import ExchangeService

from app.services.upbit.upbit_market_data import upbit_market_data_generate
from app.services.upbit.upbit_current_market_data import upbit_current_market_data_generate

from app.services.virtual_trade import virtual_trade

# 세션
from app.repositories.DBController import trade_insert

# 모델
from app.models.user import UserInformation
from app.models.trading import TradingHistory

# 토큰계산
import tiktoken

LLM_MODEL = {
    "GPT_5.0_mini": gpt_5_mini,
    "GROK_3.0_mini": grok_3_mini,
    "GEMINI_3.0_flash_preview": gemini_3_flash_preview,
    "GEMINI_2.5_pro": gemini_2_5_pro
}

## Main Process  

# api 호출 및 검증
def verify_msg(msg_dict):
    # position 확인: 문자열
    if 'position' not in msg_dict or not isinstance(msg_dict['position'], dict):
        return False
    for v in msg_dict['position'].values():
        if not isinstance(v, str):
            return False

    # why 확인: 문자열
    if 'why' not in msg_dict or not isinstance(msg_dict['why'], dict):
        return False
    for v in msg_dict['why'].values():
        if not isinstance(v, str):
            return False

    # buy_percent 확인: 숫자
    if 'buy_percent' not in msg_dict or not isinstance(msg_dict['buy_percent'], dict):
        return False
    for v in msg_dict['buy_percent'].values():
        if not isinstance(v, (int, float)):
            return False

    # sell_percent 확인: 숫자
    if 'sell_percent' not in msg_dict or not isinstance(msg_dict['sell_percent'], dict):
        return False
    for v in msg_dict['sell_percent'].values():
        if not isinstance(v, (int, float)):
            return False

    return True 
    

# datetime 체크
def datetime_ok(dates: list, interval, userid):
    try:
        dt_list = [isoparse(d) for d in dates]

        # 0~13 interval 체크
        tolerance_seconds=1
        for i in range(13):
            diff = dt_list[i+1] - dt_list[i]
            if abs(diff.total_seconds() - interval) > tolerance_seconds:
                print(f"{userid} time {i} ~ {i+1} error")
                return False

        # 13 → 14 날짜와 시간(hour)만 체크
        dt13, dt14 = dt_list[13], dt_list[14]
        last_diff_seconds = (dt14 - dt13).total_seconds()
        if abs(last_diff_seconds) > interval:
            print(f"{userid} time 13 ~ 14 error: interval too large ({last_diff_seconds}s)")
            return False

        return True

    except Exception as e:
        print(e)
        return False
    
def flow_main(user:UserInformation, 
              current_time:datetime, 
              userid:str, 
              exchange:str, 
              usemodel:str, 
              trade_fee:int,
              api_key:str, 
              ticker:list, 
              user_prompt:str, 
              _trade_history:TradingHistory, 
              trade_interval=int,
              user_logger=None): 
    
    # 백테스팅
    svc:ExchangeService = EXCHANGE_MAP[exchange]

    # 이미 앞에서 검사중이라 데이터 오류가 생길 수 없음
    userinfo:dict = {}
    userinfo = svc.user_info(
        trade_history=_trade_history,
        user_prompt=user_prompt,
        )

    # userinfo 추가
    userinfo['current_time'] = current_time.isoformat()
    userinfo['exchange'] = exchange
    userinfo['currency'] = "KRW"
    userinfo['trade_fee'] = trade_fee
    
    if not userinfo:
        print("userinfo 생성 오류")
        return False

    if trade_interval == 1800:  # 30분 거래
        intervals = [
            1800,    # 메인 신호용 30분봉
            3600,    # 단기 추세 확인용 1시간봉
            14400,   # 중기 추세 4시간봉
            86400    # 장기 추세 일봉
        ]
    elif trade_interval == 3600:  # 1시간 거래
        intervals = [
            3600,    # 메인 1시간봉
            14400,   # 중기 4시간봉
            86400    # 장기 일봉
        ]
    elif trade_interval == 14400:  # 4시간 거래
        intervals = [
            14400,   # 메인 4시간봉
            86400    # 장기 일봉
        ]
    elif trade_interval == 86400:  # 1일 거래
        intervals = [
            86400    # 메인 일봉
        ]
    else:
        user_logger.log(f"{userid} : trade_interval 오류")
        return False
    
    # Market Data - LLM 진행
    market_data_process = False   
    for i in range(ATTEMP):
        user_logger.log(f"{i} / {ATTEMP} MARKET DATA GENERATION.....")
        try:
            # Market Data
            combined_dict = {}
            # user별 lock을 통해 cach 공유
            for coin in ticker:
                
                # 1시간 4시간 일봉 제공
                for interval in intervals:
                    history_df_chunk = upbit_market_data_generate(
                        coin=coin,
                        interval=interval, 
                        currency="KRW",
                        mapping=MAPPING,
                        current_time=current_time,
                        user_logger=user_logger
                    )

                    combined_dict[f"interval_{interval}_{coin}"] = history_df_chunk
                    
                # indicator 요구조건에 맞지않은 데이터 길이는 다시 생성
                for key, val in combined_dict.items():
                    if len(val) < 350:
                        raise ValueError(f"{userid} 코인 데이터 부족: {key}")

            # indicator
            market_data = {}
            for key, df_chunk in combined_dict.items():
                market_data[key] = indicater_generate(df_chunk=df_chunk)
            
            if not market_data:
                raise ValueError(f"{userid} market_data 생성 실패") 

            def custom_dump(v):
                if isinstance(v, dict):
                    v_copy = {}
                    for k1, v1 in v.items():
                        if isinstance(v1, dict):
                            # v1 안의 v2는 한 줄로
                            v1_copy = {}
                            for k2, v2 in v1.items():
                                if isinstance(v2, list):
                                    # 리스트는 한 줄로
                                    v1_copy[k2] = "[" + ",".join(map(str, v2)) + "]"
                                else:
                                    v1_copy[k2] = v2
                            # v1 전체는 indent=None 스타일 → 문자열화하지 않고 dict 그대로 두기
                            v_copy[k1] = v1_copy
                        else:
                            v_copy[k1] = v1
                    # v 수준만 indent=2
                    return json.dumps(v_copy, ensure_ascii=False, indent=2)
                else:
                    return json.dumps(v, ensure_ascii=False)

            # 예시 호출
            market_data_str = custom_dump(market_data)

            # 공통 부분
            # 버그 생길일 없음
            prompt_text = PromptGeneration(market_data_str=market_data_str, 
                                        userinfo=userinfo, 
                                        current_time=current_time, 
                                        user_prompt=user_prompt, 
                                        ticker=ticker, 
                                        trade_interval=trade_interval,
                                        user_logger=user_logger).prompt_generation()

            print(f"{userid} Success! prompt text generation")

            # api 호출
            # 논리 상으로는 새로운 데이터로 다시 msg 진행해야됨
            msg_dict = None

            func = LLM_MODEL[usemodel]
            msg = func(api_key=api_key, prompt_text=prompt_text, userid=userid, user_logger=user_logger)

            msg = msg.replace("```json", "").replace("```", "")

            msg_dict = json.loads(msg)

            # msg_dict 값이 None 일경우
            if msg_dict == None:
                raise ValueError(f"{userid} msg 생성 실패") 

            # 딕셔너리인지 검증 실패할 경우
            if not verify_msg(msg_dict):
                raise ValueError(f"{userid} msg verify 실패") 

            print(f"{userid} : Success! msg_dict generate")  

            market_data_process= True
            break
        except Exception as e:
            tb = traceback.format_exc()
            print(f"{userid} Error:\n{tb}")
            print(f"{userid} : error : {e}")
        finally:
            time.sleep(1)
    
    # 모든 횟수 초과시 False 반환
    if not market_data_process:
        return False
    
    # Trade
    # 내부 재시도 로직 추가

    print("virtual_trade")
    result_ord, available_cash, avg_list, owner_coin, total = virtual_trade(msg=msg_dict, userinfo=userinfo, market_data=market_data, trade_interval=trade_interval)

    print("virtual_trade success")
    user_logger.log(f"prompt : \n{prompt_text}")
    user_logger.log(f"msg dict : \n{json.dumps(msg_dict, ensure_ascii=False, indent=2)}")    
    user_logger.log(f"Trade Confirmation : \n{json.dumps(result_ord, indent=2)}")

    user_logger.log(f"{userid} : Success! trade generate")

    # Wallet
    insert_data:dict = {
        "userid":userid,
        "createdtime":current_time,
        "why":msg_dict['why'],
        "position":msg_dict['position'],
        "exchange":exchange,
        "trade_history":result_ord,
        "available_cash":available_cash,
        "avg_list" : avg_list,
        "owner_coin" : owner_coin,
        "total" : total
    }

    print("insert_data")
    
    trade_insert(userid=userid, data=insert_data)

    return True
