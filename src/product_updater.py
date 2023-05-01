import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException
from time import sleep
import enum
from mysql.connector import connect, Error
from queries import Queries

SRC_URL = 'https://www.svyaznoy.ru/catalog/phone/225/apple'
CHROME_DRIVER_PATH = '../chrome-driver/chromedriver.exe'
CHROME_PROFILE_PATH = r"user-data-dir=C:\\Users\\йцу\\AppData\\Local\\Google\\Chrome\\User Data\\"
CHROME_PROFILE_DIR_NAME = '--profile-directory=Default'
DB_USER = 'root'
DB_PASS = '1111'
DB_NAME = 'svyaznoy_iphone_data'


class ElemXpath(enum.Enum):
    next_page = "//li[contains(@class, 'last')]"
    product_info = "//span[contains(@class, 'b-product-block__name')]"
    product_price = "//span[contains(@class, 'b-product-block__visible-price ')]"


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
        return int(driver.find_element(By.XPATH, ElemXpath.next_page.value).text)
    except NoSuchElementException:
        print('Failed to determine the number of pages.')


def get_url_for_page(page_num):
    return SRC_URL + '/page-' + str(page_num)


def get_products_info(driver):
    products_info = driver.find_elements(By.XPATH, ElemXpath.product_info.value)
    return [product_info.text for product_info in products_info]


def norm_price(price):
    price = price.replace(' ', '')
    price = price.replace('руб.', '')
    return int(price)


def get_products_price(driver):
    products_price = driver.find_elements(By.XPATH, ElemXpath.product_price.value)
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
    return product_info[ind_left:ind_right]


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


def update_db(products):
    try:
        with connect(
                host='localhost',
                user=DB_USER,
                password=DB_PASS,
                database=DB_NAME
        ) as connection:
            with connection.cursor() as cursor:
                cursor.executemany(Queries.insert_iphones.value, products)
                connection.commit()
    except Error as e:
        print(e)


def get_products_from_db():
    try:
        with connect(
                host='localhost',
                user=DB_USER,
                password=DB_PASS,
                database=DB_NAME
        ) as connection:
            with connection.cursor() as cursor:
                cursor.execute(Queries.get_all_iphones.value)
                res = cursor.fetchall()
                return res
    except Error as e:
        print(e)


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
    db_products = get_products_from_db()
    a = 1
    # update_db(products)


if __name__ == '__main__':
    main()
