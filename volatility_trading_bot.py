import datetime
import math

import config
import db_helper
import utils
from coins import binance

# 익절률 | 손절률
take_profit_rate = 1.4
loss_cut_rate = - 1.3

# 레버리지
leverage = 10


def exec_trading(symbol, now):
    global take_profit_rate, loss_cut_rate, leverage
    try:
        # 포지션 상태
        trading_data = db_helper.select_db_trading(symbol)
        '''
         'symbol' : symbol
         'side' : long / short
         'amount' : 주문 수량 (float)
         'order_price' : 주문 가격 (float)
         'order_time' : 주문 시간 (string)
         'op_mode' : 포지션 가능 여부 ( 1 -> 진입 | 0 -> 진입 X )
         'split_rate' : 분할 매도 비율 (float)
        '''

        # 현재가
        coin = binance.fetch_ticker(symbol=symbol)
        cur_price = float(coin['last'])

        # btc 20일선 이격률
        btc_sma20_sep_rate = utils.calc_btc_sma20_sep_rate()

        # target
        data = db_helper.select_db_target(symbol=symbol)
        long_target = data['long_target']
        short_target = data['short_target']

        # 포지션 종료
        if trading_data['op_mode'] == 1 and trading_data['side'] != 'None':

            # 주문시간과 현재시간의 차이
            order_time = trading_data['order_time']
            order_time = datetime.datetime.strptime(order_time, "%Y-%m-%d %H:%M:%S.%f")
            time_diff = now - order_time

            # 수익률
            pnl = utils.calc_pnl(trading_data, cur_price)

            # 롱 포지션에서 btc sma20 음전 | 숏 포지션에서 btc sma20 양전
            reversal = False
            if trading_data['side'] == 'long':
                reversal = btc_sma20_sep_rate < 0
            elif trading_data['side'] == 'short':
                reversal = btc_sma20_sep_rate > 0

            # 1시간봉 기준
            # 포지션을 잡은 후 1시간 이내
            if time_diff.seconds <= 3600:
                # 1시간 이내에 익절 구간있으면 익절
                # 수익률이 목표수익률 * 분할매도비율 이상이면
                # 수량의 25% 청산
                # 분할매도비율 10% 증가
                if pnl > take_profit_rate * trading_data['split_rate']:
                    liquidation_amount = math.trunc(trading_data['amount'] / 5)

                    # 주문가가 5달러 이하일 경우 주문 오류 => 전량 주문으로 변경
                    if liquidation_amount * cur_price < 5:
                        liquidation_amount = trading_data['amount']

                    trading_data = utils.exit_position(
                        exchange=binance,
                        symbol=symbol,
                        position=trading_data,
                        pnl=pnl,
                        amount=liquidation_amount
                    )


            # 포지션 잡은 후 1시간 ~ 4시간 사이
            elif 3600 + 10 < time_diff.seconds < 3600 * 4:
                # 수익률 도달시 모든 포지션 종료
                if pnl > take_profit_rate:
                    liquidation_amount = trading_data['amount']
                    trading_data = utils.exit_position(
                        exchange=binance,
                        symbol=symbol,
                        position=trading_data,
                        pnl=pnl,
                        amount=liquidation_amount
                    )

            # 포지션 잡은 후 4시간 이상이면 모든 포지션 종료
            elif time_diff.seconds >= 3600 * 4:
                liquidation_amount = trading_data['amount']
                trading_data = utils.exit_position(
                    exchange=binance,
                    symbol=symbol,
                    position=trading_data,
                    pnl=pnl,
                    amount=liquidation_amount
                )

            # 손절 시나리오
            # 손실률 loss_cut_rate 발생시 청산
            # btc sma 양전 / 음전 시 청산
            if pnl < loss_cut_rate or reversal:
                liquidation_amount = trading_data['amount']
                trading_data = utils.exit_position(
                    exchange=binance,
                    symbol=symbol,
                    position=trading_data,
                    pnl=pnl,
                    amount=liquidation_amount
                )

            # 포지션 진입
        if trading_data['op_mode'] == 1 and trading_data['side'] == 'None':
            # 잔고
            balance = binance.fetch_balance()
            usdt = balance['total']['USDT']
            # 구매 가능 자산
            amount = utils.cal_amount(usdt, cur_price, leverage)

            utils.enter_position(exchange=binance,
                                 symbol=symbol,
                                 cur_price=cur_price,
                                 long_target=long_target,
                                 short_target=short_target,
                                 amount=amount,
                                 )

        # 콘솔 프린트
        if 0 <= now.second % 10 <= 1:
            print(now)
            # 포지션이 없는 경우
            if trading_data['side'] == 'None':
                print(
                    "symbol:", symbol,
                    "현재가 :", cur_price,
                    "롱 목표가 :", long_target,
                    "숏 목표가 :", short_target, '\n'
                                             "BTC 20일선 이격률 :", btc_sma20_sep_rate,
                    "RSI14 :", utils.rsi_binance(config.TIME_FRAME, symbol),
                    "op_mode :", trading_data['op_mode']
                )
                print("# " * 100, '\n')
            # 포지션이 있는 경우
            else:
                print(
                    "symbol:", symbol,
                    "진입시간 :", trading_data['order_time'],
                    "포지션 :", trading_data['side'],
                    "주문가 :", trading_data["order_price"],
                    "주문수량 :", trading_data['amount'],
                    "현재가 :", cur_price, '\n'
                                        "수익률 :", utils.calc_pnl(trading_data, cur_price),
                    "BTC 20일선 이격률 :", btc_sma20_sep_rate,
                    "op_mode :", trading_data['op_mode']
                )
                print("# " * 100, '\n')

    except Exception as e:
        print("Main Error : ", e)
        utils.telegramMassageBot(e)
