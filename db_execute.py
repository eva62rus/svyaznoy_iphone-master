from mysql.connector import connect, Error
from queries import *

try:
    with connect(
            host="localhost",
            user='root',
            password='1111',
            database='svyaznoy_iphone_data'
    ) as connection:
        with connection.cursor() as cursor:
            cursor.execute(Queries.GET_IPHONES.value)
            res = cursor.fetchall()
            for row in res:
                print(row)

except Error as e:
    print(e)
