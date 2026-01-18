# pandas
import pandas as pd
import numpy as np

# ta
from ta.momentum import RSIIndicator, StochasticOscillator
from ta.trend import MACD, EMAIndicator, ADXIndicator
from ta.volatility import BollingerBands, AverageTrueRange
from ta.volume import OnBalanceVolumeIndicator

def indicater_generate(df_chunk: pd.DataFrame):
    df = df_chunk.copy()

    # 원화 거래라 어차피 양수
    for col in ['open', 'high', 'low', 'close']:
        if col in df.columns:
            df[col] = df[col].astype(int)

    # index -> date 컬럼 (UTC ISO 문자열)
    df['date'] = df.index.to_series().apply(lambda x: x.isoformat())

    # RSI
    df['RSI_7_x100'] = RSIIndicator(close=df['close'], window=7).rsi() * 100
    df['RSI_14_x100'] = RSIIndicator(close=df['close'], window=14).rsi() * 100

    # MACD
    macd = MACD(close=df['close'], window_fast=12, window_slow=26, window_sign=9)
    df['MACD_12_26_9'] = macd.macd()

    # Stochastic
    stoch = StochasticOscillator(high=df['high'], low=df['low'], close=df['close'], window=14, smooth_window=3)
    df['STOCHk_14_3_3_x100'] = stoch.stoch() * 100
    df['STOCHd_14_3_3_x100'] = stoch.stoch_signal() * 100

    # Bollinger Bands
    bb = BollingerBands(close=df['close'], window=5, window_dev=2)
    df['BBM_5_2.0_2.0'] = bb.bollinger_mavg()
    df['BBU_5_2.0_2.0'] = bb.bollinger_hband()
    df['BBL_5_2.0_2.0'] = bb.bollinger_lband()

    # ADX / ATR
    adx = ADXIndicator(high=df['high'], low=df['low'], close=df['close'], window=14)
    df['ADX_14_x100'] = adx.adx() * 100
    atr = AverageTrueRange(high=df['high'], low=df['low'], close=df['close'], window=14)
    df['ATRr_14'] = atr.average_true_range()

    # EMA
    for w in [20, 50, 100]:
        df[f'EMA_{w}'] = EMAIndicator(close=df['close'], window=w).ema_indicator()

    # 이동평균
    ma_windows = [20, 60, 120, 240]
    for w in ma_windows:
        df[f"MA{w}"] = df['close'].rolling(window=w).mean()

    # OBV
    df['OBV'] = OnBalanceVolumeIndicator(close=df['close'], volume=df['volume']).on_balance_volume()

    # NaN / inf 제거
    df = df.replace([np.inf, -np.inf], np.nan)
    df.dropna(subset=df.columns[df.columns.str.contains('_')], inplace=True)

    # 최신 15개
    df_latest = df.tail(15).copy()

    for col in ['BBM_5_2.0_2.0','BBU_5_2.0_2.0','BBL_5_2.0_2.0', 
                'RSI_7_x100','RSI_14_x100', 'MACD_12_26_9', 
                'STOCHk_14_3_3_x100','STOCHd_14_3_3_x100',
                'ADX_14_x100', 'ATRr_14', 
                'EMA_20', 'EMA_50', 'EMA_100',                
                'MA20', 'MA60', 'MA120', 'MA240',
                ]:
        df_latest[col] = df_latest[col].astype(int)

    # 컬럼 순서 지정
    cols_order = [
        'date', 'open', 'high', 'low', 'close', 'volume',
        'RSI_7_x100', 'RSI_14_x100', 'MACD_12_26_9',
        'STOCHk_14_3_3_x100', 'STOCHd_14_3_3_x100',
        'BBM_5_2.0_2.0', 'BBU_5_2.0_2.0', 'BBL_5_2.0_2.0',
        'ADX_14_x100', 'ATRr_14',
        'EMA_20', 'EMA_50', 'EMA_100',
        'MA20', 'MA60', 'MA120', 'MA240',
        'OBV'
    ]

    # 컬럼별 리스트로 변환 (순서 유지)
    market_data = {col: df_latest[col].tolist() for col in cols_order if col in df_latest.columns}

    return market_data
