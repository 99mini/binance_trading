import math
import datetime
import requests

import db_helper
from coins import *
from main import *

timeframe = TIME_FRAME
limit = DATA_LEN


# 타겟 계산
def calc_target(exchange, symbol):
    try:
        # 거래소에서 symbol에 대한 ohlcv 열기
        coin_ohlcv = exchange.fetch_ohlcv(
            symbol=symbol,
            timeframe=timeframe,
            since=None,
            limit=limit
        )

        df = pd.DataFrame(
            data=coin_ohlcv,
            columns=['datetime', 'open', 'high', 'low', 'close', 'volume']
        )

        previous_data = df.iloc[-2]
        now_data = df.iloc[-1]

        # noise 계산
        noise_ratio = calc_noise_ratio(period=13, df=df)
        # 반올림 고려 최소 가격 변화
        # 참조 : https://www.binance.com/en/trade-rule
        min_price_movement = 4  # SANDUSDT 의 최소 가격 변화 = 0.0001
        # 직전 봉과 지금 봉으로 타겟 계산
        long_target = round(now_data['open'] + (previous_data['high'] - previous_data['low']) * noise_ratio,
                            min_price_movement)
        short_target = round(now_data['open'] - (previous_data['high'] - previous_data['low']) * noise_ratio,
                             min_price_movement)
        return long_target, short_target
    except Exception as e:
        print("calc_target", e)
        telegramMassageBot("calc_target" + str(e))


# 주문 수량 계산
def cal_amount(usdt_balnce, cur_price, leverage):
    try:
        # 10% 비중으로 매수
        portion = 0.1

        usdt_trade = usdt_balnce * leverage * portion

        # 최소 거래 수량
        # 참조 : https://www.binance.com/en/trade-rule
        mininum_trade_amount = 1

        # 최소 주문 가능 수량 소수점 계산
        amount = math.floor((usdt_trade * mininum_trade_amount) / cur_price) / mininum_trade_amount
        return amount
    except Exception as e:
        print("cal_amount", e)
        telegramMassageBot("cal_amount" + str(e))


# 포지션 진입
def enter_position(exchange, symbol, cur_price, long_target, short_target, amount, position):
    try:

        # rsi14 가 70보다 크거나 30보다 작으면 매매를 하지 않는다.
        rsi14 = rsi_binance(timeframe, symbol)
        if rsi14 > 70 or rsi14 < 30:
            print("rsi에 의해 거래 없음")
            return cur_price, position

        btc_sma20_sep_rate = calc_btc_sma20_sep_rate()
        # btc over sma20
        # long position
        if btc_sma20_sep_rate > 0.5:
            if cur_price > long_target:
                now = datetime.datetime.now()

                position['type'] = 'long'
                position['amount'] = amount
                position['time'] = now
                position['order_price'] = cur_price

                print("=" * 100)
                print(now)
                print("long position order")
                print("amount : ", amount, "order price : ", cur_price)

                # 텔레그렘 알림
                msg = 'LONG POSITION ORDER\n수량 : {0}\n주문가격 : {1}'.format(amount, cur_price)
                telegramMassageBot(msg)

                exchange.create_market_buy_order(symbol=symbol, amount=amount)  # 바이낸스 시장가 long order
                # exchange.create_limit_buy_order(symbol=symbol, amount=amount, price=cur_price)  # 바이낸스 지정가 long order

                # db insert
                dict_data = {
                    'symbol': symbol,
                    'side': position['type'],
                    'price': cur_price,
                    'quantity': amount,
                    'fee': calc_fee(cur_price),
                    'pnl': 0,
                    'trade_time': now,
                }
                db_helper.insert_db_history(dict_data)

        # btc under sma20
        # short position
        elif btc_sma20_sep_rate < -0.5:
            if cur_price < short_target:
                now = datetime.datetime.now()

                position['type'] = 'short'
                position['amount'] = amount
                position['time'] = now
                position['order_price'] = cur_price

                print("=" * 100)
                print(now)
                print("short position order")
                print("amount : ", amount, "order price : ", cur_price)

                # 텔레그렘 알림
                msg = 'SHORT POSITION ORDER\n수량 : {0}\n주문가격 : {1}'.format(amount, cur_price)
                telegramMassageBot(msg)

                exchange.create_market_sell_order(symbol=symbol, amount=amount)  # 바이낸스 시장가 short order

                # db insert
                dict_data = {
                    'symbol': symbol,
                    'side': position['type'],
                    'price': cur_price,
                    'quantity': amount,
                    'fee': calc_fee(cur_price),
                    'pnl': 0,
                    'trade_time': now,
                }
                db_helper.insert_db_history(dict_data)

        return cur_price, position

    except Exception as e:
        print("enter_position", e)
        telegramMassageBot("enter_position" + str(e))


# 포지션 청산
def exit_position(exchange, symbol, position, amount):
    try:
        # 현재가격
        coin = exchange.fetch_ticker(symbol=symbol)
        cur_price = coin['last']

        if position['type'] == 'long':
            exchange.create_market_sell_order(symbol=symbol, amount=amount)  # 바이낸스 시장가 long liquidation
            position['amount'] -= amount

            print_console_exit_position(cur_price, position['type'])

            if position['amount'] == 0:
                position['type'] = None


        elif position['type'] == 'short':
            exchange.create_market_buy_order(symbol=symbol, amount=amount)  # 바이낸스 시장가 short liquidation
            position['amount'] -= amount

            print_console_exit_position(cur_price, position['type'])

            if position['amount'] == 0:
                position['type'] = None

        else:
            return cur_price, position

        return cur_price, position
    except Exception as e:
        print("exit_position", e)
        telegramMassageBot("exit_position" + str(e))


# 청산 주문
def exec_exit_order(exchange, symbol, position, pnl_rate_list, pnl_price_list, pnl, amount):
    try:
        # 콘솔용 포지션 변수
        tmp_position = position.copy()

        liquidation_price, position = exit_position(exchange, symbol, position, amount)

        # 콘솔용 계산식
        # TODO pnl_rate_list
        pnl_rate_list.append(pnl)
        pnl_price_list.append(pnl * amount)

        now = datetime.datetime.now()
        print(now)
        print("주문가: ", tmp_position["order_price"],
              "청산가: ", liquidation_price,
              "포지션: ", tmp_position["type"],
              "거래 수수료: ", calc_fee(liquidation_price) * tmp_position["amount"], '\n',
              "당 거래 수익률: ", pnl,
              "당 거래 수익금: ", pnl * tmp_position["amount"],
              "수익률 합계: ", sum(pnl_rate_list),
              "수익금 합계: ", sum(pnl_price_list)
              )

        # 텔레그램 알림
        msg = '수익률: {0}'.format(pnl)
        telegramMassageBot(msg)

        # db insert
        side = 'long'
        if tmp_position['type'] == 'long':
            side = 'short'
        else:
            pass
        dict_data = {
            'symbol': symbol,
            'side': side,
            'price': liquidation_price,
            'quantity': tmp_position["amount"],
            'fee': calc_fee(liquidation_price),
            'pnl': pnl * tmp_position["amount"] - calc_fee(liquidation_price),
            'trade_time': now,
        }
        db_helper.insert_db_history(dict_data)

        return position, pnl_rate_list, pnl_price_list
    except Exception as e:
        print("exec_exit_order : ", e)


# 비트코인 20일선 이격률 계산
def calc_btc_sma20_sep_rate():
    try:
        sma20 = df_btc["close"].rolling(20).mean()
        curr_btc = binance.fetch_ticker(symbol='BTC/USDT')
        cur_price = curr_btc['last']
        return round((cur_price / sma20.iloc[-1]) * 100 - 100, 3)
    except Exception as e:
        print("calc_btc_sma20_sep_rate", e)
        telegramMassageBot("calc_btc_sma20_sep_rate" + str(e))


# rsi 계산기
def rsi_calc(ohlc: pd.DataFrame, period: int = 14):
    try:
        ohlc = ohlc[4].astype(float)
        delta = ohlc.diff()
        gains, declines = delta.copy(), delta.copy()
        gains[gains < 0] = 0
        declines[declines > 0] = 0

        _gain = gains.ewm(com=(period - 1), min_periods=period).mean()
        _loss = declines.abs().ewm(com=(period - 1), min_periods=period).mean()

        RS = _gain / _loss
        return pd.Series(100 - (100 / (1 + RS)), name="RSI")
    except Exception as e:
        print("rsi_calc", e)
        telegramMassageBot("rsi_calc" + str(e))


def rsi_binance(itv, symbol):
    try:
        binance = ccxt.binance()
        ohlcv = binance.fetch_ohlcv(symbol=symbol, timeframe=itv, limit=200)
        df = pd.DataFrame(ohlcv)
        rsi = rsi_calc(df, 14).iloc[-1]
        return round(rsi, 3)
    except Exception as e:
        print("rsi_binance", e)
        telegramMassageBot("rsi_binance" + str(e))


# pnl 계산
def calc_pnl(position, liquidation_price):
    try:
        pnl = float(liquidation_price) / float(position["order_price"]) * 100 - 100
        if position["type"] == 'long':
            pass
        elif position["type"] == 'short':
            pnl *= -1

        return round(pnl, 4)
    except Exception as e:
        print("calc_pnl", e)
        telegramMassageBot("calc_pnl" + str(e))


# noise ratio 계산
def calc_noise_ratio(period, df):
    try:
        # 노이즈 = 1 - 절댓값(시가-종가)  / (고가-저가)
        # noise = 1 - abs(previous_data['open'] - previous_data['close']) / (previous_data['high'] - previous_data['low'])
        sum_noise = 0
        for i in range(2, period + 2):
            tmp_data = df.iloc[-i]
            sum_noise += 1 - abs(tmp_data['open'] - tmp_data['close']) / (tmp_data['high'] - tmp_data['low'])
        noise_ratio = round(sum_noise / period, 4)
        return noise_ratio
    except Exception as e:
        print('calc_noise_ratio', e)

# fee 계산
def calc_fee(price):
    # 거래 수수료율
    # 가격 x 수수료
    fee_rate = 0.0004
    fee = price * fee_rate
    return fee


# 텔레그램 메세지 보내기
def telegramMassageBot(msg):
    params = {'chat_id': telebotid, 'text': msg}
    # 텔레그램으로 메시지 전송
    try:
        requests.get(teleurl, params=params)
    except:
        print('telegram error')


# 포지션 청산 콜솔 프린트
def print_console_exit_position(cur_price, side):
    print("=" * 100)
    now = datetime.datetime.now()
    print(now)
    print("{0} position liquidation".format(side))
    print("liquidation price : ", cur_price)

    # 텔레그렘 알림
    msg = '{0} POSITION LIQUIDATION\n청산가격 : {1}'.format(str(side).upper(), cur_price)
    telegramMassageBot(msg)
