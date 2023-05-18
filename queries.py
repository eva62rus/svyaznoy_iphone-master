import enum


class Queries(enum.Enum):
    CREATE_DB = 'CREATE DATABASE IF NOT EXISTS svyaznoy_iphone_data'
    VIEW_ALL_DB = 'SHOW DATABASES'
    CREATE_TABLE_IPHONE = 'CREATE TABLE IF NOT EXISTS iphone(' \
                          'id INT AUTO_INCREMENT PRIMARY KEY,' \
                          'name VARCHAR(100),' \
                          'memory VARCHAR(100),' \
                          'color VARCHAR(100),' \
                          'price INT)'
    VIEW_TABLE_IPHONE = 'DESCRIBE iphone'
    REMOVE_TABLE_IPHONE = 'DROP TABLE iphone'
    INSERT_IPHONES = 'INSERT INTO iphone' \
                     '(name, memory, color, price)' \
                     'VALUES(%s, %s, %s, %s)'
    GET_IPHONES = 'SELECT name, memory, color, price FROM iphone'
    REMOVE_IPHONES = 'DELETE FROM iphone'

