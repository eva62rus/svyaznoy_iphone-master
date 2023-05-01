import enum


class Queries(enum.Enum):
    create_database = 'CREATE DATABASE svyaznoy_iphone_data'
    show_databases = 'SHOW DATABASES'
    create_table_iphone = 'CREATE TABLE iphone(' \
                          'id INT AUTO_INCREMENT PRIMARY KEY,' \
                          'name VARCHAR(100),' \
                          'memory VARCHAR(100),' \
                          'color VARCHAR(100),' \
                          'price INT)'
    show_table_iphone = 'DESCRIBE iphone'
    delete_table_iphone = 'DROP TABLE iphone'
    insert_iphones = 'INSERT INTO iphone' \
                     '(name, memory, color, price)' \
                     'VALUES(%s, %s, %s, %s)'
    get_all_iphones = 'SELECT * FROM iphone'
    remove_all_iphones = 'DELETE FROM iphone'

