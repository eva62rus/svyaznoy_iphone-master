from mysql.connector import connect, Error
from queries import *

try:
    with connect(
            host='127.0.0.1',
            user='root',
            password='1111',
            port='8080',
            database='svyaznoy_iphone_data'
    ) as connection:
        with connection.cursor() as cursor:
            cursor.execute(Queries.GET_IPHONES_BY.value, ('Apple iPhone 14 Plus', '512GB', 'белый', 120000, 127000))
            res = cursor.fetchall()
            for row in res:
                print(row)

except Error as e:
    print(e)
