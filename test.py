import time

from main import *
import datetime
import utils

symbol = "SAND/USDT"

long_target, short_target = utils.calc_target(binance, symbol)

# 잔고
balance = binance.fetch_balance()
usdt = balance['total']['USDT']

print(datetime.datetime.now())
print(symbol)
print("잔고 : ", usdt)
print("long target : ", long_target, "short target : ", short_target)
print("기준 봉 : ", utils.timeframe)
print("==============================================================")

position = {
    "type": None,
    "amount": 0
}

op_mode = True

# 콘솔 테스트용
order_price = 0
liquidation_price = 0
pnl_list = []

coin = binance.fetch_ticker(symbol=symbol)
cur_price = coin['last']
print("cur_price : ", cur_price)
print(type(cur_price))
amount = utils.cal_amount(usdt, cur_price)
print(amount)


order_price, position = utils.enter_position(binance, symbol, cur_price, long_target, short_target, amount, position)
print(order_price)
print(position)
time.sleep(5)
liquidation_price = utils.exit_position(binance,symbol,position)
print(liquidation_price)