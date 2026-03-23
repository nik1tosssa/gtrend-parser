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
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains

from webdriver_manager.chrome import ChromeDriverManager
from config_reader import config

# Настройка логирования
logging.basicConfig(level=logging.INFO)


def get_driver():
    chrome_options = Options()

    # Загрузка профиля из конфига
    user_data_dir = config.chrome_user_dir_path.get_secret_value()
    if user_data_dir:
        user_data_dir = user_data_dir.strip('"').strip("'")
        chrome_options.add_argument(f"--user-data-dir={user_data_dir}")
        chrome_options.add_argument("--profile-directory=Default")

    # Технические флаги для стабильности
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

    try:
        print(f"Navigating to comparison: {url}")
        driver.get(url)
        time.sleep(2)
        wait = WebDriverWait(driver, 20)

        print("Waiting for chart to render SVG-charts...")
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "svg")))
        time.sleep(3)

        print("Scrolling to tables container...")
        try:
            # Используем более надежный относительный путь к контейнеру таблиц
            container_xpath = "/html/body/c-wiz/div/div[5]/main/center/c-wiz/div/div[2]/div[1]/div[8]"
            container = wait.until(EC.presence_of_element_located((By.XPATH, container_xpath)))

            # Скроллим так, чтобы контейнер оказался в центре экрана
            driver.execute_script("arguments[0].scrollIntoView({behavior: 'auto', block: 'center'});", container)

            # Даем время на подгрузку данных (Lazy Load)
            driver.execute_script("window.scrollTo(0, 2000);")

            time.sleep(3)

        except Exception as e:
            print(f"Could not scroll to container: {e}")
            # Резервный вариант: скролл на фиксированное расстояние

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
    # /html/body/c-wiz/div/div[5]/main/center/c-wiz/div/div[2]/div[1]/div[8]/div/div[3]/div

    xpath1 = "/html/body/c-wiz/div/div[5]/main/center/c-wiz/div/div[2]/div[1]/div[8]/div/div[3]/div/div[1]/div[3]/div/div[1]/table/tbody[2]/tr"
    first_rows = driver.find_elements(By.XPATH, xpath1)
    first_table_keys = get_keys_from_table(first_rows)

    xpath2 = "/html/body/c-wiz/div/div[5]/main/center/c-wiz/div/div[2]/div[1]/div[8]/div/div[3]/div/div[2]/div[3]/div/div[1]/table/tbody[2]/tr"
    second_rows = driver.find_elements(By.XPATH, xpath2)
    second_table_keys = get_keys_from_table(second_rows)

    new_keys = list(set(first_table_keys + second_table_keys))
    return new_keys

def get_keys_from_table(rows) -> list[Any]:
    keys_from_table = []
    for row in rows:
        try:
            value = row.find_element(By.XPATH, "./td[2]/div[1]/span[1]").get_attribute("textContent")
            keys_from_table.append(value)
        except Exception as e:
            print(f"Error: {e}")

    return keys_from_table

def get_first_pair_values(driver) -> list[Any]:
    xpath_svg = "/html/body/c-wiz/div/div[5]/main/center/c-wiz/div/div[2]/div[1]/div[7]/div/div/div[2]//*[local-name()='svg']//*[local-name()='g'][2]//*[local-name()='g'][3]//*[local-name()='text']"

    elements = driver.find_elements(By.XPATH, xpath_svg)
    values = [elements[1].get_attribute("textContent"), elements[2].get_attribute("textContent")]

    return values


# Пример запуска
if __name__ == "__main__":
    target_url = "https://trends.google.com/explore?q=vivo%2Chuawei&date=today%203-m&geo=RU"
    data = get_google_trends_data(target_url)
    print(f"Final Result: {data}")
