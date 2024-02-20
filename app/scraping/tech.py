from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import re


class WebScraper:
    def __init__(self):
        # Настройка опций для Chrome браузера
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
            wait = WebDriverWait(self.driver, 25)
            search_input = wait.until(EC.visibility_of_element_located((By.NAME, "text")))
            search_input.clear()
            search_input.send_keys(product_name)
            search_input.send_keys(Keys.ENTER)
        except Exception as ex:
            print("Ошибка в вводе:", ex)


    def find_products(self, desired_product_count=30):
        products_info = []
        wait = WebDriverWait(self.driver, 100)
        product_count = 0

        while product_count < desired_product_count:
            # Плавный скроллинг
            self.driver.execute_script("window.scrollBy(0, 400);")
            time.sleep(1)  # Пауза, чтобы дать время на прогрузку элементов

            # Поиск товаров после каждой итерации скролла
            products_on_page = self.driver.find_elements(By.XPATH, "//div[@data-index]")
            for i in range(len(products_on_page)):
                if product_count >= desired_product_count:
                    break

                try:
                    product_xpath = f"//div[@data-index='{i}']"
                    product_element = wait.until(EC.visibility_of_element_located((By.XPATH, product_xpath)))

                    try:
                        price_element = product_element.find_element(By.XPATH,
                                                                     ".//span[@data-auto='price-value'] | .//h3[@data-auto='snippet-price-current']")
                        price_text = price_element.text.strip()
                        price_numbers = re.findall(r'\d+', price_text.replace("\u202f", "").replace(" ", ""))
                        price = ''.join(price_numbers)
                        if price:
                            price = f"{int(price):,}".replace(",", " ") + " ₽"
                        else:
                            price = "Цена не найдена"
                    except Exception as e:
                        price = "Цена не найдена"

                    store_name = "Магазин не найден"
                    try:
                        store_element = product_element.find_element(By.CSS_SELECTOR,
                                                                     "span._32ild._25-ND._66nxG._3WROT.Qg8Jj._1wKPk")
                        store_name = store_element.text.strip()
                    except Exception as e:
                        pass

                    link = "Ссылка не найдена"
                    try:
                        link_element = product_element.find_element(By.CSS_SELECTOR, "a.egKyN._2Fl2z")
                        link = link_element.get_attribute('href')
                    except:
                        pass

                    products_info.append((store_name, price, link))
                    product_count += 1
                except Exception as ex:
                    pass

                if product_count >= desired_product_count:
                    break

        return products_info


    def close_browser(self):
        self.driver.close()
        self.driver.quit()


