import ccxt
import pandas as pd

from config import *

binance = ccxt.binance(config={
    'apiKey': api_key,
    'secret': secret,
    'enableRateLimit': True,
    'options': {
        'defaultType': 'future'
    }
})



btc = binance.fetch_ohlcv(
    symbol="BTC/USDT",
    timeframe=TIME_FRAME,
    since=None,
    limit=DATA_LEN
)

sand = binance.fetch_ohlcv(
    symbol="SAND/USDT",
    timeframe=TIME_FRAME,
    since=None,
    limit=DATA_LEN
)

sand_day = binance.fetch_ohlcv(
    symbol="SAND/USDT",
    timeframe='1d',
    since=None,
    limit=DAY_LEN
)

mana = binance.fetch_ohlcv(
    symbol="MANA/USDT",
    timeframe=TIME_FRAME,
    since=None,
    limit=DATA_LEN,
)

mana_day = binance.fetch_ohlcv(
    symbol="MANA/USDT",
    timeframe='1d',
    since=None,
    limit=DAY_LEN
)

# BTC dataFrame
df_btc = pd.DataFrame(btc, columns=['datetime', 'open', 'high', 'low', 'close', 'volume'])
df_btc['datetime'] = pd.to_datetime(df_btc['datetime'], unit='ms')

# SAND dataFrame
df_sand_day = pd.DataFrame(sand_day, columns=['datetime', 'open', 'high', 'low', 'close', 'volume'])
df_sand_day['datetime'] = pd.to_datetime(df_sand_day['datetime'], unit='ms')

df_sand = pd.DataFrame(sand, columns=['datetime', 'open', 'high', 'low', 'close', 'volume'])
df_sand['datetime'] = pd.to_datetime(df_sand['datetime'], unit='ms')
df_sand['long'] = ""
df_sand['short'] = ""

# MANA DataFrame

df_mana_day = pd.DataFrame(mana_day, columns=['datetime', 'open', 'high', 'low', 'close', 'volume'])
df_mana_day['datetime'] = pd.to_datetime(df_mana_day['datetime'], unit='ms')
# df_mana_day.set_index('datetime', inplace=True)

df_mana = pd.DataFrame(mana, columns=['datetime', 'open', 'high', 'low', 'close', 'volume'])
df_mana['datetime'] = pd.to_datetime(df_mana['datetime'], unit='ms')
# df_mana.set_index('datetime', inplace=True)
df_mana['long'] = ""
df_mana['short'] = ""

