import os.path
import sqlite3

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(BASE_DIR, 'coins.db')

con = sqlite3.connect('coins.db', timeout=50000, isolation_level=None, check_same_thread=False)
con.row_factory = sqlite3.Row


def select_db_history():
    try:
        cs = con.cursor()
        cs.execute("SELECT * FROM trade_history")
        rows = cs.fetchall()
        target = rows[-1]
        cs.close()
        if target:
            return dict(target)
        else:
            return False
    except Exception as e:
        print("select_db_history: ", e)


def select_db_trading(symbol):
    try:
        cs = con.cursor()
        cs.execute("SELECT * FROM trading_table WHERE symbol = ?",(symbol,))
        target = cs.fetchone()
        cs.close()
        return dict(target)
    except Exception as e:
        print("select_db_trading: ", e)


def insert_db_history(dict_data):
    try:
        cs = con.cursor()
        cs.execute(
            "INSERT INTO trade_history VALUES(:id,:order_time,:symbol,:side,:price,:quantity)",
            {
                'order_time': dict_data['order_time'],
                'symbol': dict_data['symbol'],
                'side': dict_data['side'],
                'price': dict_data['price'],
                'quantity': dict_data['quantity'],
                'id': None
            }
        )
        cs.close()
    except Exception as e:
        print("insert_db_history: ", e)


def insert_db_trading(dict_data):
    try:
        cs = con.cursor()
        cs.execute(
            "INSERT INTO trading_table VALUES(:symbol,:side,:price,:quantity)",
            {
                'symbol': dict_data['symbol'],
                'side': dict_data['side'],
                'price': dict_data['price'],
                'quantity': dict_data['quantity'],
            }
        )
        cs.close()
    except Exception as e:
        print("insert_db_trading: ", e)


def update_db_trading(dict_data):
    try:
        cs = con.cursor()

        cs.execute(
            "UPDATE trading_table SET side=:side,price=:price, quantity=:quantity WHERE symbol=:symbol",
            {'side': dict_data['side'],
             'price': dict_data['price'],
             'quantity': dict_data['quantity'],
             'symbol': dict_data['symbol']
             }
        )

        cs.close()
    except Exception as e:
        print("update_db_trading: ", e)


def delete_db_history(id):
    try:
        cs = con.cursor()
        cs.execute("DELETE FROM trade_history WHERE id=:id", {'id': id})
        cs.close()
    except Exception as e:
        print("delete_db_history: ", e)


def delete_db_trading(symbol):
    try:
        cs = con.cursor()
        cs.execute("DELETE FROM trade_history WHERE symbol=:symbol", {'symbol': symbol})
        cs.close()
    except Exception as e:
        print('delete_db_trading', e)


# trade_history DB 전부 제거
def delete_db_all(table):
    try:
        cs = con.cursor()
        sql = "DELETE FROM {0}".format(table)
        cs.execute(sql)
        cs.close()
    except Exception as e:
        print('delete_db_all', e)
