import pandas as pd
import time
import pyupbit

from datetime import datetime, timedelta
from app.core.globals import ATTEMP

# 누락

def check_missing_data_and_fill(df_chunk: pd.DataFrame, interval: int = 3600, coin: str = None, method='ffill'):
    if df_chunk is None or df_chunk.empty:
        print(f"{coin or ''} - df_chunk가 비어있음")
        return None

    # 인덱스 정렬 및 UTC 통일
    df_chunk = df_chunk.sort_index()
    df_chunk.index = df_chunk.index.tz_convert('UTC') if df_chunk.index.tzinfo else df_chunk.index.tz_localize('UTC')

    # 기대 delta
    expected_delta = pd.Timedelta(seconds=interval)

    # tolerance: interval 길이에 따라 조정
    if interval <= 3600:
        tolerance = pd.Timedelta(minutes=1)
    elif interval <= 14400:
        tolerance = pd.Timedelta(minutes=5)
    else:
        tolerance = pd.Timedelta(minutes=10)

    # interval 단위로 모든 시간 인덱스 생성
    full_index = pd.date_range(start=df_chunk.index[0],
                               end=df_chunk.index[-1],
                               freq=pd.Timedelta(seconds=interval),
                               tz='UTC')

    # 리샘플링
    df_chunk = df_chunk.reindex(full_index)

    # 누락 구간 감지
    missing = df_chunk[df_chunk.isna().any(axis=1)]
    if not missing.empty:
        # 보간 처리
        if method == 'ffill':
            df_chunk.ffill(inplace=True)   # pandas 최신 방식
        elif method == 'linear':
            df_chunk.interpolate(method='linear', inplace=True)

    return df_chunk

def upbit_market_data_generate(coin: str, currency: str, interval: int, mapping: dict, current_time: datetime, user_logger=None):
    interval_str = mapping[interval]

    df_chunk: pd.DataFrame = None
    attempts = ATTEMP + 20
        
    for attempt in range(attempts):
        try:
            df1 = pyupbit.get_ohlcv(
                f"{currency}-{coin}", 
                interval=interval_str, 
                to=current_time, 
                count=200
                )
            
            if df1 is None or df1.empty:
                time.sleep(1)
                continue
            time.sleep(1)

            oldest_time = df1.index[0]
            df2 = pyupbit.get_ohlcv(
                f"{currency}-{coin}", 
                interval=interval_str, 
                to=oldest_time - timedelta(seconds=interval), 
                count=200
                )

            if df2 is not None and not df2.empty:
                df_chunk = pd.concat([df2, df1])
            else:
                df_chunk = df1

            # 중복 제거
            df_chunk = df_chunk[~df_chunk.index.duplicated(keep='first')]

            # timezone 처리
            if isinstance(df_chunk.index, pd.DatetimeIndex):
                if df_chunk.index.tz is None:
                    df_chunk.index = df_chunk.index.tz_localize('Asia/Seoul').tz_convert('UTC')
                else:
                    df_chunk.index = df_chunk.index.tz_convert('UTC')
            
            break

        except Exception as e:
            if attempt > 20:
                print(f"bithumb_market_data_generate for {coin} (attempt {attempt+1}): {e}")
            time.sleep(1)
    
    if df_chunk is None or df_chunk.empty:
        print(f"bithumb_market_data_generate failure for {coin}")
        return None

    df_chunk_filled = check_missing_data_and_fill(df_chunk, interval=interval, coin='BTC', method='ffill')

    return df_chunk_filled