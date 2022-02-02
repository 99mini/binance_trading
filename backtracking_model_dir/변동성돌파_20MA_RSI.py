import matplotlib.pyplot as plt
import mpl_finance
import numpy as np
import talib as ta

from coins import *

LONG_K = 0.4
SHORT_K = 0.7
# btc 데이터프레임 수정
# df_btc.drop(index=range(20), inplace=True)
df_btc["sma20"] = ta.SMA(np.asarray(df_btc['close']),20)
df_btc["sma20 separation rate"] = (df_btc["close"] / df_btc["sma20"]) * 100 - 100


# pd.set_option('display.max_columns', None)  ## 모든 열을 출력한다.
# 데이터프레임 수정
df_sand["range"] = df_sand["high"] - df_sand["low"]
df_sand["long_target"] = df_sand["open"] + df_sand["range"].shift(1) * LONG_K
df_sand["short_target"] = df_sand["open"] - df_sand["range"].shift(1) * SHORT_K
df_sand["rsi14"] = ta.RSI(np.asarray(df_sand['close']),14)

position = False
long_position = False
short_position = False
long_order_price = 0
short_order_price = 0
long_pnl = []
short_pnl = []

btc_over_sma20 = False

for i in range(20, DATA_LEN-4):
    sleep = 1
    # 포지션 청산
    # long 포지션인 경우
    if long_position and df_sand.loc[i - sleep, "long"] == 1:
        df_sand.loc[i, "long"] = -1
        long_pnl.append((df_sand.loc[i, "open"] / long_order_price) * 100 - 100)
        print("SAND LONG POSITION LIQUIDATION")
        print("청산가격 : ", df_sand.loc[i, "open"])
        print("수익률 : ", (df_sand.loc[i, "open"] / long_order_price) * 100 - 100)

        long_position = not long_position

    # short 포지션인 경우
    if short_position and df_sand.loc[i - sleep, "short"] == 1:
        df_sand.loc[i, "short"] = -1
        short_pnl.append(
            100 - (df_sand.loc[i, "open"] / short_order_price) * 100)
        print("SAND SHORT POSITION LIQUIDATION")
        print("청산가격 : ", df_sand.loc[i, "open"])
        print("수익률 : ",
              100 - (df_sand.loc[i, "open"] / short_order_price) * 100)
        short_position = not short_position

    # 포지션을 잡을 때 btc 20일 선 위에 있으면 long
    #                        아래에 있으면 short
    if df_sand.loc[i,"rsi14"] > 70 or df_sand.loc[i,"rsi14"] < 30:
        print(i)
        print("==============rsi14==============")
        print(df_sand.loc[i,"rsi14"])
        continue

    # btc over sma20
    if df_btc.loc[i,"sma20 separation rate"] > 0:
        btc_over_sma20 = True
    else:
        btc_over_sma20 = False

    # when btc over sma20, sand 변동성 돌파 전략 long order
    if btc_over_sma20:
        if df_sand.loc[i,"high"] > df_sand.loc[i,"long_target"]:
            if not df_sand.loc[i,"long"] and not long_position:
                df_sand.loc[i,"long"] = 1
                long_order_price = df_sand.loc[i,"long_target"]
                long_position = not long_position

                print(i)
                print("비트코인 20일선 이격률: ", df_btc.loc[i, "sma20 separation rate"])
                print("SAND LONG POSITION")
                print("구매가격 : ", df_sand.loc[i, "long_target"])


    # when btc under sma20, sand 변동성 돌파 전략 short order
    if not btc_over_sma20:
        if df_sand.loc[i,"low"] < df_sand.loc[i,"short_target"]:
            if not df_sand.loc[i,"short"] and not short_position:
                df_sand.loc[i,"short"] = 1
                short_order_price = df_sand.loc[i,"short_target"]
                short_position = not short_position

                print(i)
                print("비트코인 20일선 이격률: ", df_btc.loc[i, "sma20 separation rate"])
                print("SAND SHORT POSITION")
                print("구매가격 : ", df_sand.loc[i, "short_target"])





print("==========long pnl==========")
print(*long_pnl, sep='\n')
print("==========short pnl==========")
print(*short_pnl, sep='\n')
print("Time Frame : ", TIME_FRAME)
print("data len : ", DATA_LEN)
print("pnl long : ", sum(long_pnl))
print("pnl short: ", sum(short_pnl))
print("long trading count : ", len(long_pnl))
print("short trading count : ", len(short_pnl))
print("total trading count : ", len(long_pnl) + len(short_pnl))
if long_pnl:
    print("long MDD : ", min([float(x) for x in long_pnl]))
if short_pnl:
    print("short MDD : ", min([float(x) for x in short_pnl]))
print("sum long n short pnl: ", sum(long_pnl)+sum(short_pnl))

# SANDUSDT long
fig = plt.figure(figsize=(24,16))
ax_main = plt.subplot2grid((5, 1), (0, 0), rowspan=3)
ax_sub = plt.subplot2grid((5, 1), (3, 0))
ax_sub2 = plt.subplot2grid((5,1), (4,0))
ax_main.set_title("Volatility Breakout with sma20 and RSI14 Model SAND/USDT Long " + str(TIME_FRAME), fontsize=24)

ax_main.grid(True)
ax_sub.grid(True)
ax_sub2.grid(True)

# main chart
mpl_finance.candlestick2_ohlc(ax_main, df_sand['open'], df_sand['high'], df_sand['low'], df_sand['close'], width=0.5, colorup='r', colordown='b', alpha=0.5)

# sand long order position
ax_main.scatter(df_sand.loc[df_sand.long == 1].index, df_sand.long_target[df_sand.long == 1],
            color='green',
            label='Long Order',
            marker='^',
            s=200,
            alpha=1)

# sand short liquidation position
ax_main.scatter(df_sand.loc[df_sand.long == -1].index, df_sand.open[df_sand.long == -1],
            color='green',
            label='Long Liquidation',
            marker='v',
            s=200,
            alpha=1)
ax_main.legend(fontsize=18,ncol=2)

# BTC sma20 separation rate graph
ax_sub.set_title("ma20 separation rate", fontsize=24)
ax_sub.plot(df_btc.index, df_btc['sma20 separation rate'])

# RSI14 graph
ax_sub2.set_title("RSI14", fontsize=24)
ax_sub2.plot(df_sand.index, df_sand['rsi14'])

plt.tight_layout()
plt.show()

# SANDUSDT short
fig = plt.figure(figsize=(24,16))
ax_main = plt.subplot2grid((5, 1), (0, 0), rowspan=3)
ax_sub = plt.subplot2grid((5, 1), (3, 0))
ax_sub2 = plt.subplot2grid((5,1), (4,0))
ax_main.set_title("Volatility Breakout with sma20 and RSI14 Model SAND/USDT Short " + str(TIME_FRAME), fontsize=24)

# main chart
mpl_finance.candlestick2_ohlc(ax_main, df_sand['open'], df_sand['high'], df_sand['low'], df_sand['close'], width=0.5, colorup='r', colordown='b', alpha=0.5)

# sand short order position
ax_main.scatter(df_sand.loc[df_sand.short == 1].index, df_sand.short_target[df_sand.short == 1],
            color='#A040CE',
            label='Short Order',
            marker='v',
            s=200,
            alpha=1)

# sand short liquidation position
ax_main.scatter(df_sand.loc[df_sand.short == -1].index, df_sand.open[df_sand.short == -1],
            color='#A040CE',
            label='Short Liquidation',
            marker='^',
            s=200,
            alpha=1)
ax_main.legend(fontsize=18,ncol=2)

# BTC sma20 separation rate graph
ax_sub.set_title("ma20 separation rate", fontsize=24)
ax_sub.plot(df_btc.index, df_btc['sma20 separation rate'])

# RSI14 graph
ax_sub2.set_title("RSI14", fontsize=24)
ax_sub2.plot(df_sand.index, df_sand['rsi14'])

plt.tight_layout()
plt.grid(True)
plt.show()
