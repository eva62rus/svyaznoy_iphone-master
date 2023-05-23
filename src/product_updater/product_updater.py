from time import sleep
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException
import enum
from mysql.connector import connect, Error, errorcode
from src.queries import Queries

SRC_URL = 'https://www.svyaznoy.ru/catalog/phone/225/apple'
CHROME_DRIVER_PATH = '../../chrome-driver/chromedriver.exe'
CHROME_PROFILE_PATH = r"user-data-dir=C:\\Users\\Victor\\AppData\\Local\\Google\\Chrome\\User Data\\"
CHROME_PROFILE_DIR_NAME = '--profile-directory=Default'
DB_HOST = '127.0.0.1'
DB_USER = 'root'
DB_PASS = '1111'
DB_NAME = 'svyaznoy_iphone_data'
DB_PORT = '8080'


class Msg(enum.Enum):
    DB_NOT_UPD = 'No change found.'
    DB_UPD = 'Database updated successful.'
    DB_ERR_USERPASS = 'Invalid username or password specified...'
    DB_NOT_FOUND = 'Database does not exist.'
    ERR_GET_PAGE_COUNT = 'Failed to determine the number of pages.'


class ElemXpath(enum.Enum):
    NEXT_PAGE = "//li[contains(@class, 'last')]"
    PRODUCT_INFO = "//span[contains(@class, 'b-product-block__name')]"
    PRODUCT_PRICE = "//span[contains(@class, 'b-product-block__visible-price ')]"


class MyDb:
    __host = None
    __user = None
    __password = None
    __database = None
    __port = None
    __connection = None
    __session = None

    def __init__(self, host, user, password, database, port):
        self.__host = host
        self.__user = user
        self.__password = password
        self.__port = port
        self.__if_db_exists()
        self.__database = database
        self.__if_table_iphone_exists()

    def __open_connection(self):
        try:
            self.__connection = connect(
                host=self.__host,
                user=self.__user,
                password=self.__password,
                database=self.__database,
                port=self.__port
            )
            self.__session = self.__connection.cursor()
        except Error as e:
            if e.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                print(Msg.DB_ERR_USERPASS.value)
            elif e.errno == errorcode.ER_BAD_DB_ERROR:
                print(Msg.DB_NOT_FOUND.value)
            else:
                print(e)

    def __close_connection(self):
        self.__session.close()
        self.__connection.close()

    def __if_db_exists(self):
        self.__open_connection()
        self.__session.execute(Queries.CREATE_DB.value)
        self.__connection.commit()
        self.__close_connection()

    def __if_table_iphone_exists(self):
        self.__open_connection()
        self.__session.execute(Queries.CREATE_TABLE_IPHONE.value)
        self.__connection.commit()
        self.__close_connection()

    def __insert_products(self, products):
        self.__open_connection()
        self.__session.executemany(Queries.INSERT_IPHONES.value, products)
        self.__connection.commit()
        self.__close_connection()

    def __read_products(self, criteria=None):
        self.__open_connection()
        if criteria is None:
            self.__session.execute(Queries.GET_IPHONES.value)
        else:
            self.__session.execute(Queries.GET_IPHONES_BY.value, criteria)
        products = self.__session.fetchall()
        self.__close_connection()
        return products

    def __remove_all_products(self):
        self.__open_connection()
        self.__session.execute(Queries.REMOVE_IPHONES.value)
        self.__connection.commit()
        self.__close_connection()

    def update_db(self, products):
        current_products = self.__read_products()
        if sorted(current_products) == sorted(products):
            print(Msg.DB_NOT_UPD.value)
        else:
            self.__remove_all_products()
            self.__insert_products(products)
            print(Msg.DB_UPD.value)

    def get_products(self, criteria=None):
        return self.__read_products(criteria)


class SvyaznoyParser:
    __driver = None

    def __init__(self, profile_path=None, profile_dir_name=None, headlees=True):
        options = Options()
        if profile_path is not None and profile_dir_name is not None:
            options.add_argument(profile_path)
            options.add_argument(profile_dir_name)
        if headlees:
            options.add_argument('--headless=new')
        self.__driver = webdriver.Chrome(options=options)

    def get_page(self, url):
        self.__driver.get(url)

    def get_page_count(self):
        try:
            return int(self.__driver.find_element(By.XPATH, ElemXpath.NEXT_PAGE.value).text)
        except NoSuchElementException:
            print(Msg.ERR_GET_PAGE_COUNT)

    def get_products_info(self):
        products_info = self.__driver.find_elements(By.XPATH, ElemXpath.PRODUCT_INFO.value)
        return [product_info.text for product_info in products_info]

    def get_products_prices(self):
        products_prices = self.__driver.find_elements(By.XPATH, ElemXpath.PRODUCT_PRICE.value)
        return [norm_price(product_price.text) for product_price in products_prices]


def get_url_for_page(page_num):
    return SRC_URL + '/page-' + str(page_num)


def norm_price(price):
    price = price.replace(' ', '')
    price = price.replace('руб.', '')
    return int(price)


def extract_name_from_product_info(product_info):
    ind = product_info.find('GB')
    if ind == -1:
        ind = product_info.find('TB')
    ind_right = product_info.rfind(' ', 0, ind)
    return product_info[0:ind_right]


def extract_memory_from_product_info(product_info):
    ind = product_info.find('GB')
    if ind == -1:
        ind = product_info.find('TB')
    ind_left = product_info.rfind(' ', 0, ind)
    ind_right = product_info.find(' ', ind_left + 1)
    return product_info[ind_left + 1:ind_right]


def extract_color_from_product_info(product_info):
    if product_info.find('PRODUCT') != -1:
        return 'красный'
    else:
        ind_left = product_info.find('(')
        ind_right = product_info.find(')', ind_left)
    return product_info[ind_left + 1:ind_right]


def parsing_products_info(products_info, products_price):
    products = []
    for product_info, product_price in zip(products_info, products_price):
        name = extract_name_from_product_info(product_info)
        memory = extract_memory_from_product_info(product_info)
        color = extract_color_from_product_info(product_info)
        products.append((name, memory, color, product_price))
    return products


def main():
    svyazoy_parser = SvyaznoyParser(CHROME_PROFILE_PATH, CHROME_PROFILE_DIR_NAME, True)
    svyazoy_parser.get_page(SRC_URL)
    page_count = svyazoy_parser.get_page_count()
    urls = [get_url_for_page(i) for i in range(1, page_count + 1)]
    products = []
    for url in urls:
        if url != SRC_URL:
            svyazoy_parser.get_page(url)
            sleep(1)
        products_info = svyazoy_parser.get_products_info()
        products_prices = svyazoy_parser.get_products_prices()
        products += parsing_products_info(products_info, products_prices)
    print(f'total porducts count: {len(products)}.')
    connection = MyDb(DB_HOST, DB_USER, DB_PASS, DB_NAME, DB_PORT)
    connection.update_db(products)


if __name__ == '__main__':
    main()
