import traceback

# 앱 내부
from app.models.trading import TradingHistory

def upbit_user_info_generation(user_prompt, trade_history:TradingHistory):
    try:
        latest_trade: TradingHistory | None = trade_history[0] if trade_history else None
        model_why = latest_trade.why or {} if latest_trade else {}
        model_position = latest_trade.position or {} if latest_trade else {}
        model_createdtime = latest_trade.createdtime
        available_cash = latest_trade.available_cash
        avg_list = latest_trade.avg_list or {}
        owner_coin = latest_trade.owner_coin or {}   
        _trade_history = latest_trade.trade_history or {}

        userinfo = {
            f"available_cash_KRW": int(available_cash),
            "average_price" : avg_list,
            "user_prompt" : user_prompt,
            "owner_coin" : owner_coin,
            "trade_history" : {
                "history_trade_timestamp" : model_createdtime.isoformat(),
                "history_position" : model_position,
                "history_why" : model_why,                
                "history_trade_confirmation" : _trade_history
                },
            "country" : "KR"
        }
    except Exception as e:
        tb = traceback.format_exc()
        print(f"Error:\n{tb}")
        print(f"error : {e}")

    return userinfo
