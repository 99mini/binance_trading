from coins import *
import matplotlib.pyplot as plt
import mpl_finance

ORDER_SEPARATION = 3.5          # 주문 이격도
LIQUIDATION_SEPARATION = 2.0    # 청산 이격도
LIMIT_PNL = 4.0                 # 익절/손절 라인

position = False
sand_position = False
mana_position = False
sand_long = False
sand_short = False
mana_long = False
mana_short = False
sand_average_price = 0
mana_average_price = 0
sand_pnl = []
mana_pnl = []

for i in range(DATA_LEN):
    separation = df_sand["percentage"].iloc[i] - df_mana["percentage"].iloc[i]
    # 포지션이 없을 경우 separation 이 ORDER_SEPARATION 보다 높으면 포지션 잡는다.
    if abs(separation) >= ORDER_SEPARATION and not position:
        sand_average_price = df_sand["close"].iloc[i]
        mana_average_price = df_mana["close"].iloc[i]
        # separation 이 양수일 때 => sand short / mana long
        if separation > 0:
            print(df_sand.index[i], "\nsand short\t|\t", "sand short average price:\t", sand_average_price)
            print("mana long\t|\t", "mana long average price:\t", mana_average_price)
            print("sand percentage - mana percentage =", separation)

            sand_short = not sand_short
            mana_long = not mana_long

            df_sand.loc[i,'short'] = 1
            df_mana.loc[i,'long'] = 1
        # separation 이 음수일 때 => sand long / mana short
        elif separation < 0:
            print(df_sand.index[i], "\nsand long\t|\t", "sand long average price:\t", sand_average_price)
            print("mana short\t|\t", "mana short average price:\t", mana_average_price)
            print("sand percentage - mana percentage =", separation)

            sand_long = not sand_long
            mana_short = not mana_short

            df_sand.loc[i,'long'] = 1
            df_mana.loc[i,'short'] = 1
        sand_position = mana_position = position = not position


    elif position:
        # 포지션이 있으면서 LIQUIDATION_SEPARATION 보다 separation 이 작으면 포지션을 청산한다.
        sand_liquidation_price = df_sand["close"].iloc[i]
        mana_liquidation_price = df_mana["close"].iloc[i]
        if abs(separation) <= LIQUIDATION_SEPARATION:
            print(df_sand.index[i])
            print("sand percentage - mana percentage =", separation)

            if sand_position:
                if sand_long:
                    print("sand long pnl : ", (sand_liquidation_price - sand_average_price) / sand_average_price * 100)
                    sand_pnl.append((sand_liquidation_price - sand_average_price) / sand_average_price * 100)
                    sand_long = not sand_long

                    df_sand.loc[i,'long'] = -1
                elif sand_short:
                    print("sand short pnl : ", (sand_average_price - sand_liquidation_price) / sand_average_price * 100)
                    sand_pnl.append((sand_average_price - sand_liquidation_price) / sand_average_price * 100)
                    sand_short = not sand_short

                    df_sand.loc[i,'short'] = -1
            if mana_position:
                if mana_short:
                    print("mana short pnl : ", (mana_average_price-mana_liquidation_price ) / mana_average_price * 100)
                    mana_pnl.append((mana_average_price - mana_liquidation_price) / mana_average_price * 100)
                    mana_short = not mana_short

                    df_mana.loc[i,'short'] = -1
                elif mana_long:
                    print("mana long pnl : ", (mana_liquidation_price - mana_average_price) / mana_average_price * 100)
                    mana_pnl.append((mana_liquidation_price - mana_average_price) / mana_average_price * 100)
                    mana_long = not mana_long

                    df_mana.loc[i,'long'] = -1

            sand_position = mana_position = position = not position

        # 두 포지션의 수익률 합계가 LIMIT_PNL 이상일 경우 청산
        if mana_position and sand_position:
            # sand long / mana short
            if sand_long and mana_short:
                sum_of_pnl = (mana_average_price-mana_liquidation_price ) / mana_average_price * 100 + (sand_liquidation_price - sand_average_price) / sand_average_price * 100
                if sum_of_pnl > LIMIT_PNL:
                    print("sand long pnl : ", (sand_liquidation_price - sand_average_price) / sand_average_price * 100)
                    sand_pnl.append((sand_liquidation_price - sand_average_price) / sand_average_price * 100)
                    sand_long = not sand_long

                    print("mana short pnl : ", (mana_average_price-mana_liquidation_price ) / mana_average_price * 100)
                    mana.append((mana_average_price - mana_liquidation_price) / mana_average_price * 100)
                    mana_short = not mana_short

            elif sand_short and mana_long:
                sum_of_pnl = (sand_average_price - sand_liquidation_price) / sand_average_price * 100 + (mana_liquidation_price - mana_average_price) / mana_average_price * 100
                if sum_of_pnl > LIMIT_PNL:
                    print("sand short pnl : ", (sand_average_price - sand_liquidation_price) / sand_average_price * 100)
                    sand_pnl.append((sand_average_price - sand_liquidation_price) / sand_average_price * 100)
                    sand_short = not sand_short

                    print("mana long pnl : ", (mana_liquidation_price - mana_average_price) / mana_average_price * 100)
                    mana.append((mana_liquidation_price - mana_average_price) / mana_average_price * 100)
                    mana_long = not mana_long

        # # 포지션이 있으면서 익절 라인 혹은 손절 라인에 진입시 청산한다.
        # # profit and loss of sand long position 이 LIMIT_PNL 이상일 경우 청산
        # if sand_long and abs((sand_liquidation_price - sand_average_price) / sand_average_price * 100) >= LIMIT_PNL:
        #     print(df_sand.index[i])
        #     print("SAND LONG 손절/익절")
        #     print("pnl: ", (sand_liquidation_price - sand_average_price) / sand_average_price * 100)
        #     sand_pnl.append((sand_liquidation_price - sand_average_price) / sand_average_price * 100)
        #     sand_long = not sand_long
        #     sand_position = not sand_position
        #
        #     df_sand.loc[i, 'long'] = -1
        #
        # # profit and loss of mana short position 이 LIMIT_PNL 이상일 경우 청산
        # if mana_short and abs((mana_average_price - mana_liquidation_price) / mana_average_price * 100) >= LIMIT_PNL:
        #     print(df_sand.index[i])
        #     print("MANA SHORT 손절/익절")
        #     print("pnl: ", ((mana_average_price - mana_liquidation_price) / mana_average_price * 100))
        #     mana_pnl.append((mana_average_price - mana_liquidation_price) / mana_average_price * 100)
        #     mana_short = not mana_short
        #     mana_position = not mana_position
        #
        #     df_mana.loc[i, 'short'] = -1
        #
        # # profit and loss of sand short position 이 LIMIT_PNL 이상일 경우 청산
        # if sand_short and abs((sand_average_price - sand_liquidation_price) / sand_average_price * 100) >= LIMIT_PNL:
        #     print(df_sand.index[i])
        #     print("SAND SHORT 손절/익절")
        #     print("pnl: ", ((sand_average_price - sand_liquidation_price) / sand_average_price * 100))
        #     sand_pnl.append((sand_average_price - sand_liquidation_price) / sand_average_price * 100)
        #     sand_short = not sand_short
        #     sand_position = not sand_position
        #
        #     df_sand.loc[i,'short'] = -1
        #
        # # profit and loss of mana long position 이 LIMIT_PNL 이상일 경우 청산
        # if mana_long and abs((mana_liquidation_price - mana_average_price) / mana_average_price * 100) >= LIMIT_PNL:
        #     print(df_sand.index[i])
        #     print("MANA LONG 손절/익절")
        #     print("pnl: ", ((mana_liquidation_price - mana_average_price) / mana_average_price * 100))
        #     mana_pnl.append((mana_liquidation_price - mana_average_price) / mana_average_price * 100)
        #     mana_long = not mana_long
        #     mana_position = not mana_position
        #
        #     df_mana.loc[i,'long'] = -1



        position = sand_position or mana_position

# 포지션이 있는 체로 종료가 되면 포지션을 가장 최신의 마감가로 청산한다.
if position:
    sand_liquidation_price = df_sand["close"].iloc[-1]
    mana_liquidation_price = df_mana["close"].iloc[-1]
    print(df_sand.index[-1], "\nsand liquidation price\t:\t", sand_liquidation_price)
    print("mana liquidation price\t:\t", mana_liquidation_price)
    print("sand percentage - mana percentage =", separation, '\n')

    if sand_long:
        sand_pnl.append((sand_liquidation_price - sand_average_price) / sand_average_price * 100)
        sand_long = not sand_long

        df_sand.loc[-1,'long'] = -1

    elif sand_short:
        sand_pnl.append((sand_average_price - sand_liquidation_price) / sand_average_price * 100)
        sand_short = not sand_short

        df_sand.loc[-1,'short'] = -1

    if mana_long:
        mana_pnl.append((mana_liquidation_price - mana_average_price) / mana_average_price * 100)
        mana_long = not mana_long

        df_mana.loc[-1,'long'] = -1
    elif mana_short:
        mana_pnl.append((mana_average_price - mana_liquidation_price) / mana_average_price * 100)
        mana_short = not mana_short

        df_mana.loc[-1,'short'] = -1

print("==========sand pnl==========")
print(*sand_pnl, sep='\n')
print("==========mana pnl==========")
print(*mana_pnl, sep='\n')
print("Time Frame : ", TIME_FRAME)
print("data len : ", DATA_LEN)
print("sum sand : ", sum(sand_pnl))
print("sum mana : ", sum(mana_pnl))
print("trading count : ", len(sand_pnl))
print("sum sand N mana pnl: ", sum(sand_pnl)+sum(mana_pnl))

# SANDUSDT
fig = plt.figure(figsize=(24,16))
ax = fig.add_subplot(1,1,1)
mpl_finance.candlestick2_ohlc(ax, df_sand['open'], df_sand['high'], df_sand['low'], df_sand['close'], width=0.5, colorup='r', colordown='b', alpha=0.5)
plt.title("Sum of PNL Model SAND/USDT " + str(TIME_FRAME))

# sand short order position
plt.scatter(df_sand.loc[df_sand.short == 1].index, df_sand.close[df_sand.short == 1],
            color='#A040CE',
            label='Short Order',
            marker='v',
            s=200,
            alpha=1)

# sand short liquidation position
plt.scatter(df_sand.loc[df_sand.short == -1].index, df_sand.close[df_sand.short == -1],
            color='#A040CE',
            label='Short Liquidation',
            marker='^',
            s=200,
            alpha=1)

# sand long order position
plt.scatter(df_sand.loc[df_sand.long == 1].index, df_sand.close[df_sand.long == 1],
            color='green',
            label='Long Order',
            marker='^',
            s=200,
            alpha=1)

# sand short liquidation position
plt.scatter(df_sand.loc[df_sand.long == -1].index, df_sand.close[df_sand.long == -1],
            color='green',
            label='Long Liquidation',
            marker='v',
            s=200,
            alpha=1)
plt.legend(fontsize=14,ncol=2)
plt.show()

# MANAUSDT
fig = plt.figure(figsize=(24,16))
ax = fig.add_subplot(1,1,1)
mpl_finance.candlestick2_ohlc(ax, df_mana['open'], df_mana['high'], df_mana['low'], df_mana['close'], width=0.5, colorup='r', colordown='b', alpha=0.5)
plt.title("Sum of PNL Model MANA/USDT " + str(TIME_FRAME))

# mana short order position
plt.scatter(df_mana.loc[df_mana.short == 1].index, df_mana.close[df_mana.short == 1],
            color='#A040CE',
            label='Short Order',
            marker='v',
            s=200,
            alpha=1)

# mana short liquidation position
plt.scatter(df_mana.loc[df_mana.short == -1].index, df_mana.close[df_mana.short == -1],
            color='#A040CE',
            label='Short Liquidation',
            marker='^',
            s=200,
            alpha=1)

# mana long order position
plt.scatter(df_mana.loc[df_mana.long == 1].index, df_mana.close[df_mana.long == 1],
            color='green',
            label='Long Order',
            marker='^',
            s=200,
            alpha=1)

# mana short liquidation position
plt.scatter(df_mana.loc[df_mana.long == -1].index, df_mana.close[df_mana.long == -1],
            color='green',
            label='Long Liquidation',
            marker='v',
            s=200,
            alpha=1)
plt.legend(fontsize=14,ncol=2)
plt.show()
