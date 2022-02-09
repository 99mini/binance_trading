import numpy as np

symbol = "SAND/USDT"
#
# long_target, short_target = utils.calc_target(binance, symbol)
#
# # 잔고
# balance = binance.fetch_balance()
# usdt = balance['total']['USDT']
#
# position = {
#     "type": "short",
#     "amount": 0,
#     "time": datetime.datetime.now()
# }
#
# op_mode = True
#
# # 콘솔 테스트용
# order_price = 10
# pnl_list = []
#
# coin = binance.fetch_ticker(symbol=symbol)
# cur_price = coin['last']
# amount = utils.cal_amount(usdt, cur_price, 20)

#
# print(datetime.datetime.now())
# print(
#     "진입시간 :", position['time'], '\n'
#     "포지션 :", position['type'],
#     "주문가 :", order_price,
#     "주문수량 :", position['amount'],
#     "현재가 :", cur_price, '\n'
#     "수익률 :", utils.calc_pnl(position, order_price, cur_price),
#     "BTC 20일선 이격률 :", utils.calc_btc_sma20_sep_rate(),
#     "op_mode :", op_mode
# )
#
# print(datetime.datetime.now())
# print(
#     "현재가 : ", cur_price,
#     "롱 목표가 : ", long_target,
#     "숏 목표가 : ", short_target, '\n'
#     "BTC 20일선 이격률 : ", utils.calc_btc_sma20_sep_rate(),
#     "RSI14 : ", utils.rsi_binance(utils.timeframe, symbol),
#     "op_mode : ", op_mode
# )
#TODO trading_table 에서 주문 시간 가져와서 시간 빼기 구현하기
