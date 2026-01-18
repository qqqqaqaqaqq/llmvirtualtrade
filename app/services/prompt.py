import json
import textwrap
import traceback

from datetime import datetime, timedelta

from app.core.globals import *


class PromptGeneration():
    def __init__(self,  market_data_str,  current_time, userinfo, user_prompt, ticker, trade_interval, user_logger=None):
        self.market_data_str = market_data_str
        self.currenttime = current_time

        self.userinfo = userinfo
        self.user_prompt = user_prompt
        self.trade_fee = userinfo['trade_fee']
        self.currency = userinfo['currency']
        
        self.exchange = userinfo['exchange']
        self.country = userinfo['country']
        self.trade_history = userinfo['trade_history']
        self.ticker = ticker
        self.mapping = MAPPING
        self.trade_interval = trade_interval

        self.user_logger = user_logger
        
    def template_generation(self):
        try:
            input_template = {
                'Account' : {
                    f'available_cash_{self.currency}' : int(self.userinfo[f'available_cash_{self.currency}']),
                    f'owner_coin' : {f"{key}" : round(float(val), 8) for key, val in self.userinfo['owner_coin'].items()},
                    f'coin_average_price' : {f"avg_{key}" : int(val) for key, val in self.userinfo['average_price'].items()},
                }
            }
            output_template = {
                'position' : {f"{self.currency}-{coin}" : "hold or sell or buy" for coin in self.ticker },
                'why' : {f"{self.currency}-{coin}" : "reason" for coin in self.ticker },
                'buy_percent' : {f"{self.currency}-{coin}" : "%" for coin in self.ticker },
                'sell_percent' : {f"{self.currency}-{coin}" : "%" for coin in self.ticker },
            }
        except Exception as e:
            tb = traceback.format_exc()
            print(f"Error:\n{tb}")
            print(f"error : {e}")

        return input_template, output_template
    
    def prompt_generation(self):
        try:
            input_template, output_template = self.template_generation()

            prompt_text = textwrap.dedent(    
            f"""
            Important Notice:
            - All trading decisions based on AI outputs are solely the responsibility of the user.
            - The AI may provide financial advice or buy/sell signals, but any resulting gains or losses are entirely at the user's risk.
            ##############################

            Setting :
            - Current Time = UTC : {self.currenttime}
            - All timestamps are in UTC
            - Exchange = {self.exchange}
            - Trade Interval (time between each trade) = {self.trade_interval}
            - Currency = {self.currency}
            ##############################

            Account :
            Your Account : {json.dumps(input_template, ensure_ascii=False, indent=2)}.
            In the Account :
            - available_cash_{self.currency} represents your available cash in {self.currency}.
            - average_price represents your coin average cost (average purchase price).
            - owner_coin represents the amount of each coin.
            ##############################

            Market Data : 
            - {self.market_data_str}.
            Market Data Interpretation Rules
            - This is MULTI-TICKER and MULTI-INTERVAL data.
            - Key name = interval_int_coin, where int represents the interval of the corresponding value.
            - For each ticker and interval, there are 15 data points: all canldes are confirmed candles.

            Scaling & Normalization (MUST APPLY BEFORE ANALYSIS)
            - Any field ending with `_x100` represents (actual_value × 100). → MUST divide by 100 before any reasoning or explanation.
            - NEVER reason, compare, or describe indicators using raw `_x100` values.
            - ALWAYS report normalized, human-readable indicator values.
            - Do the math step-by-step for normalization before reasoning
            ##############################
            Output Template (You must return the response in exactly this format):
            {json.dumps(output_template, ensure_ascii=False, indent=2)}
            #####
            Previous Trading Actions (Reference Only):

            The following data represents the actions you took in the previous trade.
            It includes your reasoning, resulting positions, and the official trade
            confirmation. Use this information strictly as historical context when
            deciding the next trade.

            Do NOT repeat or reverse previous actions unless market conditions clearly justify it.
            {json.dumps(self.trade_history, ensure_ascii=False, indent=2)}
            ##############################

            Strategy :
            - {self.user_prompt}
            ##############################
                
            Action : 
            For each ticker, use confirmed candles [0~14] to predict next candles, then trade according to the strategy.
            Fill in position, why, buy_percent, and sell_percent
            ##############################

            Rules : 
            - Output strictly according to the provided template.
            - Account for {self.trade_fee} (%) when trade.
            - Minimum transaction amount: 5,500 {self.currency}.
            - Default: conservative investment, adjust based on user strategy.
            - Specify expected target and stop-loss prices for each coin.
            - "buy", "sell", or "hold" (string only) when filling the postition field.
            - integer %; total buy ≤ available_cash_{self.currency} when filling buy_percent field.
            - Only buy if available_cash_{self.currency} > 0 when filling buy_percent field.
            - Sum of buy_percent across all coins ≤ 100%            
            - integer % per coin; ≤ 100% for each coin when filling sell_percent field.
            - Only sell if coin balance > 0
            - All template fields (position, buy_percent, sell_percent, why) MUST be filled; empty fields are invalid.
            - buy_percent and sell_percent MUST be integers only, NOT strings or percentages with "%".
            ##############################
                
            Signal : 
            - You must return only template exactly as provided and must not add anything extra.
            - Do not use ```json``` or any other code wrappers.
            - Think at least 3 times carefully before returning the template.
            - My country is {self.country} (ISO 3166-1 alpha-2).
            - When filling the "why" field in the Output Template, you must write a human-readable explanation of the reasoning behind the selected position in the primary language used in that country. """)
        except Exception as e:
            tb = traceback.format_exc()
            print(f"Error:\n{tb}")
            print(f"error : {e}")
        
        return prompt_text