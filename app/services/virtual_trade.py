import traceback
from decimal import Decimal, ROUND_DOWN

QTY_FMT = Decimal('0.00000000')
KRW_FMT = Decimal('1')

def D(x):
    """float / int / str → Decimal 안전 변환"""
    return Decimal(str(x))


def virtual_trade(msg: dict, userinfo: dict, market_data, trade_interval):
    available_cash = D(userinfo.get('available_cash_KRW', 0))

    # 🔹 저장용은 float
    avg_list: dict = userinfo.get('average_price', {})
    owner_coin: dict = userinfo.get('owner_coin', {})

    buy_sector = msg.get('buy_percent', {})
    sell_sector = msg.get('sell_percent', {})

    result_ord = {}

    try:
        # =========================
        # BUY
        # =========================
        for coin_name, percent in buy_sector.items():
            if percent <= 0:
                continue

            coin = coin_name.split("-")[1]

            bid_total_price = (
                available_cash * D(percent) / D(100)
            ).quantize(KRW_FMT, rounding=ROUND_DOWN)

            if bid_total_price < D(5000):
                continue

            current_price = D(
                market_data[f"interval_{trade_interval}_{coin}"]["close"][-1]
            )

            quantity = (bid_total_price / current_price).quantize(
                QTY_FMT, rounding=ROUND_DOWN
            )

            if quantity <= 0:
                continue

            # 현금 차감
            available_cash -= bid_total_price

            prev_qty = D(owner_coin.get(coin, 0.0))
            prev_avg = D(avg_list.get(coin, 0.0))

            # 평단
            if prev_qty == 0:
                new_avg = current_price
            else:
                new_avg = (
                    prev_avg * prev_qty + bid_total_price
                ) / (prev_qty + quantity)

            # 🔹 저장은 float
            owner_coin[coin] = float((prev_qty + quantity).quantize(QTY_FMT))
            avg_list[coin] = float(new_avg.quantize(KRW_FMT))

            result_ord[coin] = {
                "ord_type": "bid",
                "price": int(current_price),
                "quantity": float(quantity),
            }

        # =========================
        # SELL
        # =========================
        for coin_name, percent in sell_sector.items():
            if percent <= 0:
                continue

            coin = coin_name.split("-")[1]
            if coin not in owner_coin:
                continue

            prev_qty = D(owner_coin[coin])

            quantity = (prev_qty * D(percent) / D(100)).quantize(
                QTY_FMT, rounding=ROUND_DOWN
            )

            if quantity <= 0:
                continue

            current_price = D(
                market_data[f"interval_{trade_interval}_{coin}"]["close"][-1]
            )

            ask_total_price = (quantity * current_price).quantize(
                KRW_FMT, rounding=ROUND_DOWN
            )

            if ask_total_price < D(5000):
                continue

            # 현금 증가
            available_cash += ask_total_price

            remain_qty = prev_qty - quantity

            if remain_qty <= 0:
                owner_coin.pop(coin, None)
                avg_list.pop(coin, None)
            else:
                owner_coin[coin] = float(remain_qty.quantize(QTY_FMT))

            result_ord[coin] = {
                "ord_type": "ask",
                "price": int(current_price),
                "quantity": float(quantity),
            }

        # =========================
        # TOTAL
        # =========================
        owner_coin_price = D(0)

        for coin, qty in owner_coin.items():
            price = D(
                market_data[f"interval_{trade_interval}_{coin}"]["close"][-1]
            )
            owner_coin_price += (
                D(qty) * price
            ).quantize(KRW_FMT, rounding=ROUND_DOWN)

        total = available_cash + owner_coin_price

    except Exception as e:
        print(traceback.format_exc())
        print("error:", e)

    # 🔹 DB 저장용 최종 반환
    return  result_ord, int(available_cash), avg_list, owner_coin, int(total)
