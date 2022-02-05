import datetime
import math
import time

import utils
from main import *

symbol = "SAND/USDT"

long_target, short_target = utils.calc_target(binance, symbol)

# 잔고
balance = binance.fetch_balance()
usdt = balance['total']['USDT']

# 코인
coin = binance.fetch_ticker(symbol=symbol)

# 레버리지
leverage = 20
binance.load_markets()
market = binance.market(symbol)
binance.fapiPrivate_post_leverage({
    'symbol': market['id'],
    'leverage': leverage
})

now = datetime.datetime.now()

print(now)
print(symbol)
print("잔고 : ", usdt)
print("long target : ", long_target, "short target : ", short_target)
print("기준 봉 : ", utils.timeframe)
print("=" * 100)

position = {
    "type": None,
    "amount": 0,
    "time": None,
    "order_price": 0
}

# True -> 주문 가능
# False -> 주문 불가능
op_mode = False

# 분할 매도 비율
split_sell_rate = 0.8

# 콘솔 테스트용
liquidation_price = 0
pnl_rate_list = []
pnl_price_list = []

# 익절률 | 손절률
take_profit_rate = 1.3
loss_cut_rate = - 1.2

utils.telegramMassageBot("{0} PROGRAM START".format(str(now)))

while True:
    try:
        # 현재 시간
        now = datetime.datetime.now()

        coin = binance.fetch_ticker(symbol=symbol)
        # 현재가
        cur_price = float(coin['last'])
        # 구매 가능 자산
        amount = utils.cal_amount(usdt, cur_price, leverage)

        # btc 20일선 이격률
        btc_sma20_sep_rate = utils.calc_btc_sma20_sep_rate()

        # 포지션 종료
        if op_mode and position['type'] is not None:

            # 주문시간과 현재시간의 차이
            time_diff = now - position['time']

            # 수익률
            pnl = utils.calc_pnl(position, cur_price)

            # 롱 포지션에서 btc sma20 음전 | 숏 포지션에서 btc sma20 양전
            reversal = False
            if position['type'] == 'long':
                reversal = btc_sma20_sep_rate < 0
            elif position['type'] == 'short':
                reversal = btc_sma20_sep_rate > 0

            # 1시간봉 기준
            # 포지션을 잡은 후 1시간 이내
            if time_diff.seconds <= 3600:
                # 1시간 이내에 익절 구간있으면 익절
                # 수익률이 목표수익률 * 분할매도비율 이상이면
                # 수량의 25% 청산
                # 분할매도비율 10% 증가
                if pnl > take_profit_rate * split_sell_rate:
                    liquidation_amount = math.trunc(position['amount'] / 5)

                    # 주문가가 5달러 이하일 경우 주문 오류 => 전량 주문으로 변경
                    if liquidation_amount * cur_price < 5:
                        liquidation_amount = position['amount']
                        op_mode = False

                    position, pnl_rate_list, pnl_price_list = utils.exec_exit_order(
                        exchange=binance,
                        symbol=symbol,
                        position=position,
                        pnl_rate_list=pnl_rate_list,
                        pnl_price_list=pnl_price_list,
                        pnl=pnl,
                        amount=liquidation_amount
                    )

                    split_sell_rate *= 1.1

            # 포지션 잡은 후 1시간 ~ 4시간 사이
            elif 3600 + 10 < time_diff.seconds < 3600 * 4:
                # 수익률 도달시 모든 포지션 종료
                if pnl > take_profit_rate:
                    liquidation_amount = position['amount']
                    position, pnl_rate_list, pnl_price_list = utils.exec_exit_order(
                        exchange=binance,
                        symbol=symbol,
                        position=position,
                        pnl_rate_list=pnl_rate_list,
                        pnl_price_list=pnl_price_list,
                        pnl=pnl,
                        amount=liquidation_amount
                    )
                    op_mode = False
            # 포지션 잡은 후 4시간 이상이면 모든 포지션 종료
            elif time_diff.seconds >= 3600 * 4:
                liquidation_amount = position['amount']
                position, pnl_rate_list, pnl_price_list = utils.exec_exit_order(
                    exchange=binance,
                    symbol=symbol,
                    position=position,
                    pnl_rate_list=pnl_rate_list,
                    pnl_price_list=pnl_price_list,
                    pnl=pnl,
                    amount=liquidation_amount
                )
                op_mode = False

                # 잔고 갱신
                balance = binance.fetch_balance()
                usdt = balance['total']['USDT']

            # 손절 시나리오
            # 손실률 loss_cut_rate 발생시 청산
            # btc sma 양전 / 음전 시 청산
            if pnl < loss_cut_rate or reversal:
                liquidation_amount = position['amount']
                position, pnl_rate_list, pnl_price_list = utils.exec_exit_order(
                    exchange=binance,
                    symbol=symbol,
                    position=position,
                    pnl_rate_list=pnl_rate_list,
                    pnl_price_list=pnl_price_list,
                    pnl=pnl,
                    amount=liquidation_amount
                )
                op_mode = False

        # 포지션이 없는 경우 목표가 갱신
        if position['type'] is None and now.minute == 0 and (10 <= now.second < 20):
            print("=" * 100)
            print("목표가 갱신")
            long_target, short_target = utils.calc_target(binance, symbol)
            op_mode = True

            time.sleep(10)

        # 포지션 진입
        if op_mode and position['type'] is None:
            order_price, position = utils.enter_position(binance,
                                                         symbol,
                                                         cur_price,
                                                         long_target,
                                                         short_target,
                                                         amount,
                                                         position
                                                         )
            split_sell_rate = 0.8

        # 콘솔 프린트
        if 0 <= now.second % 10 <= 1:
            print(now)
            # 포지션이 없는 경우
            if position['type'] is None:
                print("현재가 :", cur_price,
                      "롱 목표가 :", long_target,
                      "숏 목표가 :", short_target, '\n'
                                               "BTC 20일선 이격률 :", btc_sma20_sep_rate,
                      "RSI14 :", utils.rsi_binance(utils.timeframe, symbol),
                      "op_mode :", op_mode
                      )
            # 포지션이 있는 경우
            else:
                print(
                    "진입시간 :", position['time'],
                    "포지션 :", position['type'],
                    "주문가 :", position["order_price"],
                    "주문수량 :", position['amount'],
                    "현재가 :", cur_price, '\n'
                                        "수익률 :", utils.calc_pnl(position, cur_price),
                    "BTC 20일선 이격률 :", btc_sma20_sep_rate,
                    "op_mode :", op_mode
                )

    except Exception as e:
        print("Main Error : ", e)
        utils.telegramMassageBot(e)

    time.sleep(1)
