import pandas as pd
import time
import requests

from app.core.globals import ATTEMP

def interval_to_upbit(interval:int):
    mapping = {
        60: "1",
        180: "3",
        300: "5",
        600: "10",
        900: "15",
        1800: "30",
        3600: "60",
        14400: "240",
        86400: "days"
    }
    return mapping[interval]


def get_ohlcv(coin:str, currency:str, interval:int, user_logger=None):
    interval_convert = interval_to_upbit(interval)
    df = None
    try:
        if interval_convert == 'days':
            url = f"https://api.upbit.com/v1/candles/days?market={currency}-{coin}&count=1"
        else :
            url = f"https://api.upbit.com/v1/candles/minutes/{interval_convert}?market={currency}-{coin}&count=1"

        headers = {"accept": "application/json"}
        response = requests.get(url, headers=headers)

        if response.status_code != 200:
            print(f"Bithumb API HTTP error for {coin}: {response.status_code}")
            return None

        try:
            data = response.json() 

        except ValueError:
            print(f"Upbit JSON decode error for {coin}: {response.text}")
            return None

        if not data or not isinstance(data, list):
            print(f"No data returned for {coin}")
            return None

        df = pd.DataFrame(data)
        df = df.rename(columns={
            "opening_price": "open",
            "high_price": "high",
            "low_price": "low",
            "trade_price": "close",
            "candle_acc_trade_volume": "volume",
            "candle_acc_trade_price": "value"
        })

        df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms", utc=True).dt.round('s')

        df.set_index("timestamp", inplace=True)

        df = df[["open", "high", "low", "close", "volume", "value"]]

        # 정렬
        df = df.sort_index()
        df.index.name = None
    except Exception as e:
        print(f"upbit current market data, {e}")
        return None
        
    return df

def upbit_current_market_data_generate(coin: str, currency: str, interval: int, user_logger=None):
    attemps = ATTEMP + 20
    for i in range(attemps):
        df_chunk:pd.DataFrame = get_ohlcv(coin=coin, currency=currency, interval=interval, user_logger=user_logger)

        if df_chunk is None:
            print(f"{coin} - get_ohlcv returned None, retry {i+1}")
            time.sleep(1)
            continue

        if df_chunk.empty:
            time.sleep(1)
            continue
        else:
            break
    
    return df_chunk


