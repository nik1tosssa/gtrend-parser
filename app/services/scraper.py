import time
import random
import logging
from typing import Any

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager import drivers

from webdriver_manager.chrome import ChromeDriverManager

from config_reader import config

# Настройка логирования
logging.basicConfig(level=logging.INFO)


def get_driver():
    chrome_options = Options()

    # user_data =config.chrome_user_dir_path.get_secret_value()

    # Загрузка профиля из конфига
    user_data_dir = config.chrome_user_dir_path.get_secret_value()
    if user_data_dir:
        user_data_dir = user_data_dir.strip('"').strip("'")
        chrome_options.add_argument(f"--user-data-dir={user_data_dir}")
        chrome_options.add_argument("--profile-directory=Default")


    # Технические флаги для стабильности
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--remote-debugging-port=9230")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")

    # Отключение флага автоматизации
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option("useAutomationExtension", False)

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)

    # Маскировка под реального пользователя
    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
        "source": "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
    })
    return driver

def get_google_trends_data(url: str):
    print("Starting scraper...")
    driver = get_driver()
    results = []
    # time.sleep(1000)
    time.sleep(random.uniform(1, 3))

    try:
        print(f"Navigating to comparison: {url}")
        driver.get(url)
        # time.sleep(2)
        wait = WebDriverWait(driver, 20)

        print("Waiting for chart to render SVG-charts...")
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "svg")))
        # time.sleep(3)

        print("Scrolling to tables container...")
        try:
            for _ in range(3):
                driver.execute_script("window.scrollTo(0, 2000);")
                time.sleep(random.uniform(1, 3))

            # time.sleep(3)

        except Exception as e:
            print(f"Could not scroll to container: {e}")

        results.append(get_first_pair_values(driver))
        results.append(get_new_keywords(driver))

    except Exception as e:
        driver.save_screenshot("debug_screen.png")
        logging.error(f"Scraper error: {e}")
    finally:
        time.sleep(1)
        driver.quit()

    return results


def get_new_keywords(driver) -> list[Any]:
    try:
        # driver = get_driver()
        # driver.get(url)
        # wait = WebDriverWait(driver, 20)
        #
        # print("Waiting for chart to render SVG-charts...")
        # wait.until(EC.presence_of_element_located((By.TAG_NAME, "svg")))
        # for _ in range(3):
        #     driver.execute_script("window.scrollTo(0, 2000);")
        #     time.sleep(random.uniform(1, 3))

        #         /html/body/div[2]/div[2]/div/md-content/div/div/div[5]/trends-widget/ng-include/widget/div/div/ng-include/div
        xpath1 = "/html/body/div[2]/div[2]/div/md-content/div/div/div[5]/trends-widget/ng-include/widget/div/div/ng-include/div/*"
        first_rows = driver.find_elements(By.XPATH, xpath1)
        first_table_keys = get_keys_from_table(first_rows)

        xpath2 = "/html/body/div[2]/div[2]/div/md-content/div/div/div[8]/trends-widget/ng-include/widget/div/div/ng-include/div/*"
        second_rows = driver.find_elements(By.XPATH, xpath2)
        second_table_keys = get_keys_from_table(second_rows)

        new_keys = list(set(first_table_keys + second_table_keys))
        # driver.quit()
        return new_keys

    except Exception as e:
        print(f"Error: {e}")


def get_keys_from_table(rows) -> list[Any]:
    keys_from_table = []
    for row in rows[::-1]:
        try:
            value = row.find_element(By.XPATH, "./div[1]/ng-include/a/div/div[2]/span").get_attribute("textContent")
            keys_from_table.append(value)
        except Exception as e:
            print(f"Error: {e}")
    if len(keys_from_table) == 0:
        keys_from_table.append('no new keys')
    return keys_from_table


def get_first_pair_values(driver) -> list:
    values = []
    try:
        # driver = get_driver()
        # driver.get(url)
        table_xpath = "//div[contains(@aria-label, 'tabular representation')]/table"

        wait = WebDriverWait(driver, 15)
        table = wait.until(EC.presence_of_element_located((By.XPATH, table_xpath)))

        first_val = table.find_element(By.XPATH, ".//tbody/tr/td[2]").get_attribute("textContent")
        second_val = table.find_element(By.XPATH, ".//tbody/tr/td[3]").get_attribute("textContent")

        # Очищаем от лишних пробелов и символов
        values = [first_val.strip(), second_val.strip()]

    except Exception as e:
        print(f"Ошибка поиска: Элемент не появился или структура изменилась.")
        # Попробуем сделать скриншот, чтобы понять, что видел Selenium в этот момент
        driver.save_screenshot("debug_screen.png")

    # driver.quit()
    return values

def get_only_first_pair_values(url) -> list:
    values = []
    try:
        driver = get_driver()
        driver.get(url)
        table_xpath = "//div[contains(@aria-label, 'tabular representation')]/table"

        wait = WebDriverWait(driver, 15)
        table = wait.until(EC.presence_of_element_located((By.XPATH, table_xpath)))

        first_val = table.find_element(By.XPATH, ".//tbody/tr/td[2]").get_attribute("textContent")
        second_val = table.find_element(By.XPATH, ".//tbody/tr/td[3]").get_attribute("textContent")

        # Очищаем от лишних пробелов и символов
        values = [first_val.strip(), second_val.strip()]
    except Exception as e:
        print(f"Ошибка поиска: Элемент не появился или структура изменилась.")
        # Попробуем сделать скриншот, чтобы понять, что видел Selenium в этот момент
        driver.save_screenshot("debug_screen.png")

    driver.quit()
    return values

# Пример запуска
if __name__ == "__main__":
    target_url = "https://trends.google.com/trends/explore?q=iphone%2Csamsung&date=today%203-m&geo=BY&cmpt=q&hl=ru"

    data = get_google_trends_data(target_url)
    print(f"Final Result: {data}")
