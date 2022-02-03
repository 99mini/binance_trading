import datetime
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
    "time": None
}

op_mode = False

# 콘솔 테스트용
order_price = 0
liquidation_price = 0
pnl_rate_list = []
pnl_price_list = []

utils.telegramMassageBot("PROGRAM START")

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

        # 일봉 기준
        # 포지션 종료
        # if now.hour == 9 and now.minute == 0 and (20 <= now.second < 30):

        '''
        # 15분봉 기준
        # 포지션 종료
        if now.minute % 15 == 1 and (0 <= now.second < 10):
            if op_mode and position['type'] is not None and (position['time'].minute / 15 != now.minute / 15):
                # 콘솔용 포지션 변수
                tmp_position = position.copy()

                liquidation_price, position = utils.exit_position(binance, symbol, position)
                op_mode = False

                # 잔고 갱신
                balance = binance.fetch_balance()
                usdt = balance['total']['USDT']

                # 콘솔용 계산식
                pnl = utils.calc_pnl(tmp_position, order_price, liquidation_price)
                pnl_rate_list.append(pnl)
                pnl_price_list.append(pnl * tmp_position["amount"])

                print(now)
                print("주문가: ", order_price,
                      "청산가: ", liquidation_price,
                      "포지션: ", tmp_position["type"],
                      "거래 수수료: ", 0.0004 * tmp_position["amount"] * 2, '\n',
                      "당 거래 수익률: ", pnl,
                      "당 거래 수익금: ", pnl * tmp_position["amount"],
                      "수익률 합계: ", sum(pnl_rate_list),
                      "수익금 합계: ", sum(pnl_price_list)
                      )

                # 텔레그램 알림
                msg = '수익률: {0}'.format(utils.calc_pnl(tmp_position, order_price, cur_price))
                utils.telegramMassageBot(msg)

        # 목표가 갱신
        if now.minute % 15 == 0 and (10 <= now.second < 20):
            print("=" * 100)
            print("목표가 갱신")
            long_target, short_target = utils.calc_target(binance, symbol)
            op_mode = True

            time.sleep(10)
        '''

        # 1시간봉 기준
        # 포지션 종료
        if op_mode and position['type'] is not None:

            time_diff = now - position['time']
            pnl = utils.calc_pnl(position, order_price, cur_price)

            reversal = False
            if position['type'] == 'long':
                reversal = btc_sma20_sep_rate < 0
            elif position['type'] == 'short':
                reversal = btc_sma20_sep_rate > 0

            # 현재시간과 포지션 진입시간의 차이가 1시간 이상이면 포지션 종료
            # 수익률 1.5% 발생시 청산
            # 손실률 1.6% 발생시 청산
            # btc sma 양전 / 음전 시 청산
            if time_diff.seconds >= 3600 * 4 or pnl > 1.5 or pnl < -1.4 or reversal:
                position, pnl_rate_list, pnl_price_list = utils.exec_exit_order(
                    exchange=binance,
                    symbol=symbol,
                    position=position,
                    pnl_rate_list=pnl_rate_list,
                    pnl_price_list=pnl_price_list,
                    pnl=pnl,
                    order_price=order_price
                )
                op_mode = False

                # 잔고 갱신
                balance = binance.fetch_balance()
                usdt = balance['total']['USDT']

        # 목표가 갱신
        if now.minute == 0 and (10 <= now.second < 20):
            print("=" * 100)
            print("목표가 갱신")
            long_target, short_target = utils.calc_target(binance, symbol)
            op_mode = True

            time.sleep(10)

        '''
        # # 4시간 봉 기준
        # # 포지션 종료
        # if now.hour % 4 == 0 and now.minute == 55 and (0 <= now.second < 10):
        #     if op_mode and position['type'] is not None and ((position['time'].hour - 1) / 4 != (now.hour - 1) / 4):
        #         liquidation_price, position = utils.exit_position(binance, symbol, position)
        #         op_mode = False
        #
        #         # 콘솔용 포지션 변수
        #         tmp_position = position.copy()
        #
        #         # 콘솔용 계산식
        #         pnl = utils.calc_pnl(tmp_position, order_price, liquidation_price)
        #         pnl_rate_list.append(pnl)
        #         pnl_price_list.append(pnl * tmp_position["amount"])
        #
        #         print(now)
        #         print("주문가: ", order_price,
        #               "청산가: ", liquidation_price,
        #               "포지션: ", tmp_position["type"],
        #               "거래 수수료: ", 0.0004 * tmp_position["amount"] * 2, '\n',
        #               "당 거래 수익률: ", pnl,
        #               "당 거래 수익금: ", pnl * tmp_position["amount"],
        #               "수익률 합계: ", sum(pnl_rate_list),
        #               "수익금 합계: ", sum(pnl_price_list)
        #               )
        #
        #         # 텔레그램 알림
        #         msg = '수익률: {0}'.format(utils.calc_pnl(tmp_position, order_price, cur_price))
        #         utils.telegramMassageBot(msg)
        #
        # # 목표가 갱신
        # if now.hour % 4 == 1 and now.minute == 0 and (20 <= now.second < 30):
        #     print("=" * 100)
        #     print("목표가 갱신")
        #     long_target, short_target = utils.calc_target(binance, symbol)
        #     op_mode = True
        #     # 잔고
        #     balance = binance.fetch_balance()
        #     usdt = balance['total']['USDT']
        #     time.sleep(10)
        '''

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

        # 콘솔 프린트
        if 0 <= now.second % 10 <= 1:
            print(now.hour, now.minute, now.second)
            # 포지션이 없는 경우
            if position['type'] is None:
                print("현재가 : ", cur_price,
                      "롱 목표가 : ", long_target,
                      "숏 목표가 : ", short_target, '\n',
                      "BTC 20일선 이격률 : ", btc_sma20_sep_rate,
                      "RSI14 : ", utils.rsi_binance(utils.timeframe, symbol),
                      "op_mode : ", op_mode
                      )
            # 포지션이 있는 경우
            else:
                print(
                    "진입시간 : ", position['time'],
                    "포지션 : ", position['type'],
                    "주문가 : ", order_price,
                    "주문수량 : ", position['amount'],
                    "현재가 : ", cur_price, '\n'
                    "수익률 : ", utils.calc_pnl(position, order_price, cur_price),
                    "BTC 20일선 이격률 : ", btc_sma20_sep_rate,
                    "op_mode : ", op_mode
                )

    except Exception as e:
        print("Main Error : ", e)
        utils.telegramMassageBot(e)

    time.sleep(1)
