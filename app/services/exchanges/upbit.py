from app.services.upbit.upbit_user import upbit_user_info_generation
from app.services.upbit.upbit_market_data import upbit_market_data_generate
from app.services.upbit.upbit_current_market_data import upbit_current_market_data_generate

class UpbitService:
    user_info = staticmethod(upbit_user_info_generation)
    market_data = staticmethod(upbit_market_data_generate)
    current_market_data = staticmethod(upbit_current_market_data_generate)
