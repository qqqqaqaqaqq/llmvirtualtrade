DEVELOPMENT = False

MAPPING ={
    300 : "minute5",
    1_800: "minute30",
    3_600: "minute60",
    14_400: "minute240",
    86_400: "day"
}

CURRENCY = {
    "Upbit" : "KRW",
    "Bithumb" : "KRW",
    "Binance" : "USD"
}

ATTEMP = 15

RUNNING_THREADS = {}

# 거래용
SPREAD_RATE = 0.02
DROP_RATE = 0.03

# 마켓데이터 길이
SEQ = 15