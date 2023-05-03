from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException
from time import sleep
import enum
from mysql.connector import connect, Error, errorcode
from queries import Queries

SRC_URL = 'https://www.svyaznoy.ru/catalog/phone/225/apple'
CHROME_DRIVER_PATH = '../chrome-driver/chromedriver.exe'
CHROME_PROFILE_PATH = r"user-data-dir=C:\\Users\\Victor\\AppData\\Local\\Google\\Chrome\\User Data\\"
CHROME_PROFILE_DIR_NAME = '--profile-directory=Default'
DB_HOST = 'localhost'
DB_USER = 'root'
DB_PASS = '1111'
DB_NAME = 'svyaznoy_iphone_data'


class ElemXpath(enum.Enum):
    NEXT_PAGE = "//li[contains(@class, 'last')]"
    PRODUCT_INFO = "//span[contains(@class, 'b-product-block__name')]"
    PRODUCT_PRICE = "//span[contains(@class, 'b-product-block__visible-price ')]"


class Msg(enum.Enum):
    DB_NOT_UPD = 'No change found.'
    DB_UPD = 'Database updated successful.'
    DB_ERR_USERPASS = 'Invalid username or password specified...'
    DB_NOT_FOUND = 'Database does not exist.'
    ERR_GET_PAGE_COUNT = 'Failed to determine the number of pages.'


class MyDb:
    __host = None
    __user = None
    __password = None
    __database = None
    __connection = None
    __session = None

    def __init__(self, host, user, password, database):
        self.__host = host
        self.__user = user
        self.__password = password
        self.__database = database

    def _open_connection(self):
        try:
            self.__connection = connect(
                host=self.__host,
                user=self.__user,
                password=self.__password,
                database=self.__database
            )
            self.__session = self.__connection.cursor()
        except Error as e:
            if e.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                print(Msg.DB_ERR_USERPASS.value)
            elif e.errno == errorcode.ER_BAD_DB_ERROR:
                print(Msg.DB_NOT_FOUND.value)
            else:
                print(e)

    def _close_connection(self):
        self.__session.close()
        self.__connection.close()

    def insert_products(self, products):
        self._open_connection()
        self.__session.executemany(Queries.INSERT_IPHONES.value, products)
        self.__connection.commit()
        self._close_connection()

    def read_products(self):
        self._open_connection()
        self.__session.execute(Queries.GET_IPHONES.value)
        products = self.__session.fetchall()
        self._close_connection()
        return products

    def remove_all_products(self):
        self._open_connection()
        self.__session.execute(Queries.REMOVE_IPHONES.value)
        self.__connection.commit()
        self._close_connection()

    def update_db(self, products):
        current_products = self.read_products()
        if sorted(current_products) == sorted(products):
            print(Msg.DB_NOT_UPD.value)
        else:
            self.remove_all_products()
            self.insert_products(products)
            print(Msg.DB_UPD.value)


def init_driver(headless, profile_path=None, profile_dir_name=None):
    options = Options()
    if profile_path is not None and profile_dir_name is not None:
        options.add_argument(profile_path)
        options.add_argument(profile_dir_name)
    if headless:
        options.add_argument('--headless=new')
    return webdriver.Chrome(options=options)


def get_page_count(driver):
    try:
        return int(driver.find_element(By.XPATH, ElemXpath.NEXT_PAGE.value).text)
    except NoSuchElementException:
        print(Msg.ERR_GET_PAGE_COUNT.value)


def get_url_for_page(page_num):
    return SRC_URL + '/page-' + str(page_num)


def get_products_info(driver):
    products_info = driver.find_elements(By.XPATH, ElemXpath.PRODUCT_INFO.value)
    return [product_info.text for product_info in products_info]


def norm_price(price):
    price = price.replace(' ', '')
    price = price.replace('руб.', '')
    return int(price)


def get_products_price(driver):
    products_price = driver.find_elements(By.XPATH, ElemXpath.PRODUCT_PRICE.value)
    return [norm_price(product_price.text) for product_price in products_price]


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
    driver = init_driver(True, CHROME_PROFILE_PATH, CHROME_PROFILE_DIR_NAME)
    driver.get(SRC_URL)
    sleep(1)
    page_count = get_page_count(driver)
    urls = [get_url_for_page(i) for i in range(1, page_count + 1)]
    products = []
    for url in urls:
        if url != SRC_URL:
            driver.get(url)
            sleep(1)
        products_info = get_products_info(driver)
        products_price = get_products_price(driver)
        products += parsing_products_info(products_info, products_price)
    print(len(products))
    connection = MyDb(DB_HOST, DB_USER, DB_PASS, DB_NAME)
    connection.update_db(products)


if __name__ == '__main__':
    main()
