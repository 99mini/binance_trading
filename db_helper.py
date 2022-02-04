import os.path
import sqlite3

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(BASE_DIR, 'coin_buy_sell.db')

con = sqlite3.connect(db_path, timeout=50000, isolation_level=None, check_same_thread=False)
con.row_factory = sqlite3.Row


def read_db_history(attribute):
    try:
        cs = con.cursor()
        cs.execute("SELECT * FROM trade_history")
        rows = cs.fetchall()
        target = rows[-1]
        cs.close()
        return target[attribute]
    except Exception as e:
        print("read_db_history: ", e)


def insert_db_history(dict_data):
    try:
        cs = con.cursor()
        cs.execute(
            "INSERT INTO trade_history VALUES(:symbol,:side,:price,:quantity,:fee,:pnl,:trade_time)",
            {
                'symbol': dict_data['symbol'],
                'side': dict_data['side'],
                'price': dict_data['price'],
                'quantity': dict_data['quantity'],
                'fee': dict_data['fee'],
                'pnl': dict_data['pnl'],
                'trade_time': dict_data['trade_time'],
                'id': None
            }
        )
        cs.close()
    except Exception as e:
        print("insert_db_history: ", e)


def update_db_history(dict_data):
    try:
        cs = con.cursor()
        cs.execute("SELECT * FROM trade_history")
        target = cs.fetchall()
        target = target[-1]

        # cs.execute(
        #     "UPDATE trade_history SET 청산시간=:청산시간,청산가=:청산가 WHERE id=:id",
        #     {'청산시간': dict_data['청산시간'],
        #      '청산가': dict_data['청산가'],
        #      'id': target['id']
        #      }
        # )

        cs.close()
    except Exception as e:
        print("update_db_history: ", e)


def delete_db_history(id):
    try:
        cs = con.cursor()
        cs.execute("DELETE FROM trade_history WHERE id=:id", {'id': id})
        cs.close()
    except Exception as e:
        print("delete_db_history: ", e)


# trade_history DB 전부 제거
def delete_db_all():
    cs = con.cursor()
    cs.execute("SELECT * FROM trade_history")
    rows = cs.fetchall()
    for row in rows:
        id = row['id']
        delete_db_history(id)
    cs.close()


# delete_db_all()
