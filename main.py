import datetime
import time

import db_helper
import utils
import volatility_trading_bot
from coins import *

symbols = ['SAND/USDT', 'MANA/USDT', 'XRP/USDT']

now = datetime.datetime.now()

print(now)
print("PROGRAM START")
print("기준 봉 : ", timeframe)
print("=" * 100)

utils.telegramMassageBot("{0}\nPROGRAM START".format(str(now)))

for symbol in symbols:
    # init setting
    # target
    long_target, short_target = utils.calc_target(binance, symbol)
    is_coin = db_helper.select_db_target(symbol=symbol)

    if is_coin:
        db_helper.update_db_target(symbol=symbol, long_target=long_target, short_target=short_target)
    else:
        db_helper.insert_db_target(symbol=symbol, long_target=long_target, short_target=short_target)

    # trading
    dict_data = {
        'symbol': symbol,
        'side': 'None',
        'quantity': 0,
        'order_price': 0,
        'op_mode': 0
    }
    is_coin = db_helper.select_db_trading(symbol=symbol)
    if is_coin:
        db_helper.update_db_trading(dict_data=dict_data)
    else:
        db_helper.insert_db_trading(dict_data=dict_data)

while True:
    now = datetime.datetime.now()
    if now.minute == 0 and (10 < now.second < 20):
        utils.update_targets(symbols=symbols)
    for symbol in symbols:
        volatility_trading_bot.exec_trading(symbol=symbol, now=now)
        time.sleep(1)