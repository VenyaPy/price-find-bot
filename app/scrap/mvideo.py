from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

class Mvideo:
    def __init__(self):
        options = webdriver.ChromeOptions()
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_experimental_option('excludeSwitches', ['enable-automation'])
        options.add_experimental_option('useAutomationExtension', False)

        # Создание сервиса для Chrome драйвера
        service = webdriver.ChromeService()
        self.driver = webdriver.Chrome(service=service, options=options)

        # Выполнение специальной команды для удаления следов автоматизации в браузере
        self.driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
            'source': '''
                        delete window.cdc_adoQpoasnfa76pfcZLmcfl_Array;
                        delete window.cdc_adoQpoasnfa76pfcZLmcfl_Promise;
                        delete window.cdc_adoQpoasnfa76pfcZLmcfl_Symbol;
                        delete window.cdc_adoQpoasnfa76pfcZLmcfl_JSON;
                        delete window.cdc_adoQpoasnfa76pfcZLmcfl_Proxy;
                        delete window.cdc_adoQpoasnfa76pfcZLmcfl_Object;
                    '''
        })


    def open_page(self, url):
        try:
            self.driver.get(url)
            time.sleep(1)
        except Exception as ex:
            print(ex)

    def search_product(self, product_name):
        try:
            wait = WebDriverWait(self.driver, 8)
            search = wait.until(EC.visibility_of_element_located((By.CLASS_NAME, 'input__field')))
            search.send_keys(product_name)
            search.send_keys(Keys.ENTER)
        except Exception as ex:
            print('Ошибка в вводе товара:', ex)

    def find_price(self):
        try:
            wait = WebDriverWait(self.driver, 10)
            price_element = wait.until(EC.visibility_of_element_located((By.CLASS_NAME, 'price__main-value')))
            price = price_element.text.strip()
            return price

        except Exception as ex:
            print('Ошибка при поиске цены', ex)
            return 'Цена не найдена'

    def show_url(self):
        try:
            wait = WebDriverWait(self.driver, 12)
            find_url = wait.until(EC.visibility_of_element_located((By.CLASS_NAME, 'product-title__text')))
            url = find_url.get_attribute('href')
            return url
        except Exception as ex:
            print("Ошибка при поиске URL", ex)
            return 'URL не найден'

    def close_browser(self):
        self.driver.close()
        self.driver.quit()





