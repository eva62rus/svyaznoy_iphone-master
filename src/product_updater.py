import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException
from time import sleep
import enum

SRC_URL = 'https://www.svyaznoy.ru/catalog/phone/225/apple'
CHROME_DRIVER_PATH = '../chrome-driver/chromedriver.exe'
CHROME_PROFILE_PATH = r"user-data-dir=C:\\Users\\Victor\\AppData\\Local\\Google\\Chrome\\User Data\\"
CHROME_PROFILE_DIR_NAME = '--profile-directory=Default'


class ElemXpath(enum.Enum):
    next_page = "//li[contains(@class, 'last')]"
    product_info = "//span[contains(@class, 'b-product-block__name')]"
    product_price = "//span[contains(@class, 'b-product-block__visible-price ')]"


class Iphone:
    def __init__(self, name, memory, color, price):
        self.name = name
        self.memory = memory
        self.color = color
        self.price = price


def init_driver(headless, profile_path, profile_dir_name):
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
    ind = product_info.find(' ')
    ind = product_info.find(' ', ind + 1)
    ind = product_info.find(' ', ind + 1)
    return product_info[0:ind]


def extract_memory_from_product_info(product_info):
    ind = product_info.find('GB')
    ind_left = product_info.rfind(' ', 0, ind)
    ind_right = product_info.find(' ', ind_left + 1)
    return product_info[ind_left:ind_right]


def extract_color_from_product_info(product_info):
    ind_left = product_info.find('(')
    ind_right = product_info.find(')', ind_left)
    return product_info[ind_left + 1:ind_right]


def parsing_products_info(products_info, products_price):
    products = []
    for product_info, product_price in zip(products_info, products_price):
        name = extract_name_from_product_info(product_info)
        memory = extract_memory_from_product_info(product_info)
        color = extract_color_from_product_info(product_info)
        iphone = Iphone(name, memory, color, product_price)
        products.append(iphone)
    return products


def main():
    driver = init_driver(True, CHROME_PROFILE_PATH, CHROME_PROFILE_DIR_NAME)
    driver.get(SRC_URL)
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
    with open('products.txt', 'a') as f:
        for product in products:
            f.write(f'Name: {product.name}, Price: {product.price}, Color: {product.color}, Mem: {product.memory}\n')


if __name__ == '__main__':
    main()
