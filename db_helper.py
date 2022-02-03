import datetime
import sqlite3
import time

con = sqlite3.connect('coin_buy_sell.db', timeout=50000, isolation_level=None, check_same_thread=False)
con.row_factory = sqlite3.Row


def read_db_history(attribute):
    try:
        cs = con.cursor()
        cs.execute("SELECT * FROM 거래내역")
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
            "INSERT INTO 거래내역 VALUES(:주문시간,:청산시간,:주문가,:청산가,:포지션,:id)",
            {
                '주문시간': dict_data['주문시간'],
                '청산시간': "",
                '주문가': dict_data['주문가'],
                '청산가': 0.0,
                '포지션': dict_data['포지션'],
                'id': None
            }
        )
        cs.close()
    except Exception as e:
        print("insert_db_history: ", e)


def update_db_history(dict_data):
    try:
        cs = con.cursor()
        cs.execute("SELECT * FROM 거래내역")
        target = cs.fetchall()
        target = target[-1]

        cs.execute(
            "UPDATE 거래내역 SET 청산시간=:청산시간,청산가=:청산가 WHERE id=:id",
            {'청산시간': dict_data['청산시간'],
             '청산가': dict_data['청산가'],
             'id': target['id']
             }
        )

        cs.close()
    except Exception as e:
        print("update_db_history: ", e)


def delete_db_history(id):
    try:
        cs = con.cursor()
        cs.execute("DELETE FROM 거래내역 WHERE id=:id", {'id': id})
        cs.close()
    except Exception as e:
        print("delete_db_history: ", e)


# 거래내역 DB 전부 제거
def delete_db_all():
    cs = con.cursor()
    cs.execute("SELECT * FROM 거래내역")
    rows = cs.fetchall()
    for row in rows:
        id = row['id']
        delete_db_history(id)
    cs.close()

# delete_db_all()
