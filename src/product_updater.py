from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException
from time import sleep
import enum

SRC_URL = 'https://www.svyaznoy.ru/catalog/phone/225/apple'
CHROME_DRIVER_PATH = '../chrome-driver/chromedriver.exe'


class ElemXpath(enum.Enum):
    next_page = "//li[contains(@class, 'last')]"
    product_info = "//span[contains(@class, 'b-product-block__name')]"
    product_price = "//span[contains(@class, 'b-product-block__visible-price ')]"


class Iphone:
    def __init__(self, name, memory, color, price):
        self.__name = name
        self.__memory = memory
        self.__color = color
        self.__price = price


def init_driver(headless):
    options = Options()
    if headless:
        options.add_argument('--headless=new')
    return webdriver.Chrome(options=options)


def get_page_count(driver):
    try:
        return int(driver.find_element(By.XPATH, ElemXpath.next_page.value).text)
    except NoSuchElementException:
        print('Failed to determine the number of pages.')


def get_products_info(driver):
    return driver.find_elements(By.XPATH, ElemXpath.product_info.value)


def get_products_price(driver):
    return driver.find_elements(By.XPATH, ElemXpath.product_price.value)


def parsing_products_info(products_info, products_price):
    for product_info, product_price in enumerate(products_info, products_price):



def main():
    driver = init_driver(headless=True)
    driver.get(SRC_URL)
    page_count = get_page_count(driver)
    products_info = get_products_info(driver)
    products_price = get_products_price(driver)
    for i in range(len(products_info)):
        print(products_info[i].text)
        print(products_price[i].text)


if __name__ == '__main__':
    main()
