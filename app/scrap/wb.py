from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

class WebBrowser:
    def __init__(self):
        options = webdriver.ChromeOptions()
        service = webdriver.ChromeService()
        self.driver = webdriver.Chrome(service=service, options=options)

    def open_page(self, url):
        try:
            self.driver.get(url)
            time.sleep(1)
        except Exception as ex:
            print(ex)

    def search_product(self, product_name):
        try:
            wait = WebDriverWait(self.driver, 8)
            search_input = wait.until(EC.visibility_of_element_located((By.CLASS_NAME, "search-catalog__input")))
            search_input.send_keys(product_name)
            search_input.send_keys(Keys.ENTER)
        except Exception as ex:
            print("Ошибка в вводе:", ex)

    def find_price(self):
        try:
            wait = WebDriverWait(self.driver, 10)
            # Ожидаем, пока элемент не станет видимым на странице
            price_element = wait.until(EC.visibility_of_element_located((By.CLASS_NAME, "price__lower-price")))
            price = price_element.text.strip()  # Используем .strip() для удаления лишних пробелов
            return price
        except Exception as ex:
            print("Ошибка при поиске цены:", ex)
            return 'Цена не найдена'

    def show_url(self):
        try:
            wait = WebDriverWait(self.driver, 12)
            find_url = wait.until(EC.visibility_of_element_located((By.CLASS_NAME, 'product-card__link')))
            url = find_url.get_attribute('href')
            return url
        except Exception as ex:
            print("Ошибка при поиске URL", ex)
            return 'URL не найден'




    def close_browser(self):
        self.driver.close()
        self.driver.quit()



