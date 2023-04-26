import enum


class Queries(enum.Enum):
    create_database = 'CREATE DATABASE svyaznoy_iphone_data'
    show_databases = 'SHOW DATABASES'
    create_table_iphone = 'CREATE TABLE iphone(' \
                          'id INT AUTO_INCREMENT PRIMARY KEY,' \
                          'name VARCHAR(100),' \
                          'memory INT,' \
                          'color VARCHAR(100))'
    show_table = 'DESCRIBE iphone'

